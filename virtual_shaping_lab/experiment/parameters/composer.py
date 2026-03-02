"""Typed parameter composition and deterministic serialization helpers."""

from __future__ import annotations

from dataclasses import is_dataclass, fields
from typing import Any, Mapping

from experiment.domain.types import TrialTimeSpec
from experiment.parameters.pipeline import ParameterNormalizerPipeline, ParameterValidatorPipeline
from experiment.parameters.types import (
    AttentionParams,
    ContextParams,
    EpsilonGreedyPolicyParams,
    ExperimentParameters,
    LearnerParams,
    NullPolicyParams,
    RepresentationParams,
    RuntimeParams,
    SalienceParams,
    SimilarityParams,
    SoftmaxPolicyParams,
    UnitParams,
)
from virtual_shaping_lab.domain.naming import normalize_protocol_key


def _to_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return float(default)


def _normalize_attention_map(attention: Mapping[str, Any] | None) -> dict[str, float]:
    if not isinstance(attention, Mapping):
        return {}
    out: dict[str, float] = {}
    for key, value in attention.items():
        if isinstance(value, Mapping) and "attention" in value:
            out[str(key)] = _to_float(value.get("attention"), 1.0)
        else:
            out[str(key)] = _to_float(value, 1.0)
    return out


def _normalize_salience_map(salience: Any) -> tuple[float, dict[str, float]]:
    if salience is None:
        return 1.0, {}
    if isinstance(salience, Mapping):
        out: dict[str, float] = {}
        for key, value in salience.items():
            if isinstance(value, Mapping) and "salience" in value:
                out[str(key)] = _to_float(value.get("salience"), 1.0)
            else:
                out[str(key)] = _to_float(value, 1.0)
        return 1.0, out
    return _to_float(salience, 1.0), {}


def _similarity_to_nested_dict(similarity: Any) -> dict[str, dict[str, float]]:
    if not isinstance(similarity, Mapping):
        return {}
    if isinstance(similarity.get("values"), list):
        values = similarity.get("values", [])
        labels = similarity.get("stimuli", [])
        if not isinstance(labels, list) or len(labels) != len(values):
            labels = [str(i) for i in range(len(values))]
        matrix: dict[str, dict[str, float]] = {}
        for i, row in enumerate(values):
            if not isinstance(row, list):
                continue
            matrix[str(labels[i])] = {}
            for j, val in enumerate(row):
                matrix[str(labels[j])] = _to_float(val, 0.0)
        return matrix
    # already dict-like map
    matrix: dict[str, dict[str, float]] = {}
    for key, inner in similarity.items():
        if not isinstance(inner, Mapping):
            continue
        matrix[str(key)] = {str(k): _to_float(v, 0.0) for k, v in inner.items()}
    return matrix


class ParameterComposer:
    """Compose validated payloads into immutable typed parameter objects."""

    @classmethod
    def compose(cls, payload: Mapping[str, Any], *, normalize_and_validate: bool = True) -> ExperimentParameters:
        if normalize_and_validate:
            normalized = ParameterNormalizerPipeline.normalize(payload)
            ParameterValidatorPipeline.validate(normalized)
        else:
            normalized = dict(payload)

        exp = normalized.get("experiment", {})
        if not isinstance(exp, Mapping):
            raise ValueError("payload.experiment must be an object")

        representation = cls._compose_representation(exp)
        learner = cls._compose_learner(exp)
        policy = cls._compose_policy(exp)
        runtime = cls._compose_runtime(exp)
        units = cls._compose_units(exp)

        return ExperimentParameters(
            representation=representation,
            learner=learner,
            policy=policy,
            runtime=runtime,
            units=tuple(units),
        )

    @staticmethod
    def _compose_representation(exp: Mapping[str, Any]) -> RepresentationParams:
        rep = exp.get("representation")
        rep_params = rep.get("params", {}) if isinstance(rep, Mapping) else {}
        if not isinstance(rep_params, Mapping):
            rep_params = {}

        context_inference = exp.get("context_inference", {})
        if not isinstance(context_inference, Mapping):
            context_inference = {}
        contexts = rep_params.get("contexts", ())
        if isinstance(contexts, list):
            context_values = tuple(str(c) for c in contexts)
        else:
            context_values = ()
        context = ContextParams(
            mode=str(rep_params.get("context_mode", "gated")),
            contexts=context_values,
            inference_enabled=bool(context_inference.get("enabled", False)),
        )

        salience_default, salience_overrides = _normalize_salience_map(exp.get("salience"))
        salience = SalienceParams(default=salience_default, overrides=salience_overrides)

        sim = rep_params.get("similarity")
        similarity = SimilarityParams(
            enabled=sim is not None,
            matrix=_similarity_to_nested_dict(sim),
        )
        return RepresentationParams(context=context, salience=salience, similarity=similarity)

    @staticmethod
    def _compose_learner(exp: Mapping[str, Any]) -> LearnerParams:
        phases = exp.get("phases", [])
        phase_params: Mapping[str, Any] = {}
        if isinstance(phases, list) and phases and isinstance(phases[0], Mapping):
            phase_params = phases[0].get("params", {}) if isinstance(phases[0].get("params", {}), Mapping) else {}
        alpha = _to_float(phase_params.get("alpha", exp.get("alpha", 0.1)), 0.1)
        gamma_raw = phase_params.get("gamma", exp.get("gamma"))
        gamma = None if gamma_raw is None else _to_float(gamma_raw, 0.0)
        attention_map = _normalize_attention_map(exp.get("attention"))
        attention = AttentionParams(
            mode="static" if attention_map else "none",
            default=1.0,
            overrides=attention_map,
        )
        return LearnerParams(
            algorithm=str(exp.get("learner", "")),
            alpha=alpha,
            gamma=gamma,
            attention=attention,
        )

    @staticmethod
    def _compose_policy(exp: Mapping[str, Any]):
        policy = exp.get("policy")
        if policy is None:
            return NullPolicyParams()
        if isinstance(policy, str):
            name = normalize_protocol_key(policy)
            if name == "softmax":
                return SoftmaxPolicyParams()
            if name == "epsilon_greedy":
                return EpsilonGreedyPolicyParams()
            return NullPolicyParams()
        if isinstance(policy, Mapping):
            name = normalize_protocol_key(str(policy.get("name", "null")))
            params = policy.get("params", {})
            if not isinstance(params, Mapping):
                params = {}
            actions = tuple(str(a) for a in params.get("actions", []) if a is not None)
            if name == "softmax":
                return SoftmaxPolicyParams(
                    temperature=_to_float(params.get("temperature", 1.0), 1.0),
                    actions=actions,
                )
            if name == "epsilon_greedy":
                return EpsilonGreedyPolicyParams(
                    epsilon=_to_float(params.get("epsilon", 0.1), 0.1),
                    actions=actions,
                )
        return NullPolicyParams()

    @staticmethod
    def _compose_runtime(exp: Mapping[str, Any]) -> RuntimeParams:
        runtime = exp.get("runtime", {})
        if not isinstance(runtime, Mapping):
            runtime = {}
        seed = runtime.get("seed")
        if seed is not None:
            try:
                seed = int(seed)
            except (TypeError, ValueError):
                seed = None
        return RuntimeParams(
            seed=seed,
            update_mode=str(runtime.get("update_mode", "trial")),
            record_mode=str(runtime.get("record_mode", "trial")),
            strict_records=bool(runtime.get("strict_records", False)),
        )

    @staticmethod
    def _compose_units(exp: Mapping[str, Any]) -> list[UnitParams]:
        phases = exp.get("phases")
        if isinstance(phases, list) and phases:
            units: list[UnitParams] = []
            for i, phase in enumerate(phases):
                if not isinstance(phase, Mapping):
                    continue
                params = phase.get("params", {})
                if not isinstance(params, Mapping):
                    params = {}
                duration = _to_float(params.get("duration_s", 1.0), 1.0)
                dt = _to_float(params.get("dt_s", 1.0), 1.0)
                time = TrialTimeSpec(duration_s=duration, dt_s=dt)
                unit_key = str(phase.get("protocol", f"unit_{i}"))
                units.append(
                    UnitParams(
                        unit_key=unit_key,
                        name=str(phase.get("name", f"Phase {i}")),
                        context_id=(str(params["context"]) if "context" in params else None),
                        n_trials=int(params.get("n_trials", 1)),
                        time=time,
                        contingency=dict(params),
                        schedule_runtime=(params.get("schedule_runtime") if isinstance(params.get("schedule_runtime"), Mapping) else None),
                        learning_gate={"enabled": bool(params.get("learning_enabled", True))},
                        metadata={"phase_index": i},
                    )
                )
            return units

        # single protocol fallback
        params = exp.get("params", {})
        if not isinstance(params, Mapping):
            params = {}
        duration = _to_float(params.get("duration_s", 1.0), 1.0)
        dt = _to_float(params.get("dt_s", 1.0), 1.0)
        time = TrialTimeSpec(duration_s=duration, dt_s=dt)
        protocol = str(exp.get("protocol", "unit"))
        return [
            UnitParams(
                unit_key=protocol,
                name="Phase 0",
                context_id=(str(params["context"]) if "context" in params else None),
                n_trials=int(params.get("n_trials", 1)),
                time=time,
                contingency=dict(params),
                schedule_runtime=(params.get("schedule_runtime") if isinstance(params.get("schedule_runtime"), Mapping) else None),
                learning_gate={"enabled": bool(params.get("learning_enabled", True))},
                metadata={"phase_index": 0},
            )
        ]


def parameters_to_dict(value: Any) -> Any:
    """Deterministic, JSON-serializable structure for composed parameters."""
    if is_dataclass(value):
        out = {}
        for f in sorted(fields(value), key=lambda item: item.name):
            out[f.name] = parameters_to_dict(getattr(value, f.name))
        return out
    if isinstance(value, dict):
        return {str(k): parameters_to_dict(v) for k, v in sorted(value.items(), key=lambda item: str(item[0]))}
    if isinstance(value, Mapping):
        return {str(k): parameters_to_dict(v) for k, v in sorted(value.items(), key=lambda item: str(item[0]))}
    if isinstance(value, (list, tuple)):
        return [parameters_to_dict(v) for v in value]
    return value

