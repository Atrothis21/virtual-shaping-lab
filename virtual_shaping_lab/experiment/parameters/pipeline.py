"""Normalization and validation pipelines for parameter composition."""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping

from virtual_shaping_lab.domain.naming import normalize_protocol_key


def _as_float(value: Any, field: str) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        raise ValueError(f"{field} must be numeric")


def _is_grid_aligned(duration_s: float, dt_s: float, tol: float = 1e-9) -> bool:
    steps = duration_s / dt_s
    return abs(steps - round(steps)) <= tol


class ParameterNormalizerPipeline:
    """Normalize draft payloads into deterministic config-like dictionaries."""

    @staticmethod
    def normalize(payload: Mapping[str, Any]) -> dict[str, Any]:
        if not isinstance(payload, Mapping):
            raise ValueError("payload must be an object")

        out = deepcopy(dict(payload))
        exp = out.setdefault("experiment", {})
        if not isinstance(exp, dict):
            raise ValueError("experiment must be an object")

        # Normalize protocol keys.
        if "protocol" in exp:
            exp["protocol"] = normalize_protocol_key(exp["protocol"])
        phases = exp.get("phases")
        if isinstance(phases, list):
            for phase in phases:
                if isinstance(phase, dict) and "protocol" in phase:
                    phase["protocol"] = normalize_protocol_key(phase["protocol"])
                params = phase.get("params") if isinstance(phase, dict) else None
                if isinstance(params, dict) and "n_trials" in params:
                    try:
                        params["n_trials"] = int(params["n_trials"])
                    except (TypeError, ValueError):
                        pass

        # Normalize policy key.
        policy = exp.get("policy")
        if isinstance(policy, dict) and "name" in policy:
            policy["name"] = normalize_protocol_key(policy["name"])

        # Runtime defaults.
        runtime = exp.setdefault("runtime", {})
        if not isinstance(runtime, dict):
            raise ValueError("experiment.runtime must be an object")
        runtime.setdefault("seed", None)
        runtime.setdefault("update_mode", "trial")
        runtime.setdefault("record_mode", "trial")
        runtime.setdefault("strict_records", False)
        runtime.setdefault("debug", False)

        return out


class ParameterValidatorPipeline:
    """Semantic and ownership-boundary validation for normalized payloads."""

    _LEAK_KEYS = {"attention", "attention_compound", "salience", "similarity"}
    _ALLOWED_ATTENTION_STRATEGIES = {"none", "static", "pearce_hall", "mackintosh"}

    @classmethod
    def validate(cls, payload: Mapping[str, Any]) -> None:
        if not isinstance(payload, Mapping):
            raise ValueError("payload must be an object")
        exp = payload.get("experiment")
        if not isinstance(exp, Mapping):
            raise ValueError("payload.experiment must be an object")

        rep = exp.get("representation")
        if rep is None:
            raise ValueError("experiment.representation is required")

        cls._validate_representation(rep, exp)
        cls._validate_attention_config(exp)
        cls._validate_attention_keys(exp, rep)
        cls._validate_runtime(exp)
        cls._validate_phases(exp)
        cls._validate_contexts(exp, rep)

    @classmethod
    def _validate_attention_config(cls, exp: Mapping[str, Any]) -> None:
        cfg = exp.get("attention_config")
        if cfg is None:
            attn = exp.get("attention")
            if isinstance(attn, Mapping) and ("name" in attn or "params" in attn):
                cfg = attn
            else:
                return
        if not isinstance(cfg, Mapping):
            raise ValueError("experiment.attention_config must be an object")
        if "name" not in cfg or "params" not in cfg:
            raise ValueError("experiment.attention_config must include 'name' and 'params'")
        name = cfg.get("name")
        if not isinstance(name, str) or not name.strip():
            raise ValueError("experiment.attention_config.name must be a non-empty string")
        if name.strip().lower() not in cls._ALLOWED_ATTENTION_STRATEGIES:
            raise ValueError(
                "Unsupported experiment.attention_config.name "
                f"'{name}'. Allowed: {', '.join(sorted(cls._ALLOWED_ATTENTION_STRATEGIES))}"
            )
        if not isinstance(cfg.get("params"), Mapping):
            raise ValueError("experiment.attention_config.params must be an object")

    @staticmethod
    def _validate_runtime(exp: Mapping[str, Any]) -> None:
        runtime = exp.get("runtime", {})
        if not isinstance(runtime, Mapping):
            raise ValueError("experiment.runtime must be an object")

        update_mode = runtime.get("update_mode", "trial")
        record_mode = runtime.get("record_mode", "trial")
        if str(update_mode) not in {"trial", "tick"}:
            raise ValueError("runtime.update_mode must be 'trial' or 'tick'")
        if str(record_mode) not in {"trial", "tick"}:
            raise ValueError("runtime.record_mode must be 'trial' or 'tick'")
        if not isinstance(runtime.get("strict_records", False), bool):
            raise ValueError("runtime.strict_records must be boolean")
        if not isinstance(runtime.get("debug", False), bool):
            raise ValueError("runtime.debug must be boolean")

    @classmethod
    def _validate_representation(cls, rep: Any, exp: Mapping[str, Any]) -> None:
        if isinstance(rep, str):
            return
        if not isinstance(rep, Mapping):
            raise ValueError("representation must be string or object")
        params = rep.get("params", {})
        if not isinstance(params, Mapping):
            raise ValueError("representation.params must be an object")
        if "attention" in params or "attention_compound" in params:
            raise ValueError("representation.params must not include attention fields")
        similarity = params.get("similarity")
        if similarity is not None:
            cls._validate_similarity(similarity)

    @staticmethod
    def _validate_similarity(similarity: Any) -> None:
        if not isinstance(similarity, Mapping):
            raise ValueError("similarity must be an object")
        if similarity.get("type") != "matrix":
            raise ValueError("similarity.type must be 'matrix'")
        values = similarity.get("values")
        if not isinstance(values, list) or not values:
            raise ValueError("similarity.values must be a non-empty matrix")
        n = len(values)
        for row in values:
            if not isinstance(row, list) or len(row) != n:
                raise ValueError("similarity.values must be a square matrix")
        for i in range(n):
            for j in range(n):
                if abs(float(values[i][j]) - float(values[j][i])) > 1e-9:
                    raise ValueError("similarity.values must be symmetric")

    @classmethod
    def _validate_attention_keys(cls, exp: Mapping[str, Any], rep: Any) -> None:
        attention = exp.get("attention")
        if attention is None:
            return
        if not isinstance(attention, Mapping):
            raise ValueError("experiment.attention must be an object")
        if "name" in attention or "params" in attention:
            # Strategy-form attention is validated by _validate_attention_config.
            return

        known_stimuli: set[str] = set()
        stimuli = exp.get("stimuli")
        if isinstance(stimuli, list):
            known_stimuli.update(str(s) for s in stimuli)
        elif isinstance(stimuli, Mapping):
            known_stimuli.update(str(k) for k in stimuli.keys())

        if isinstance(rep, Mapping):
            params = rep.get("params", {})
            if isinstance(params, Mapping):
                rep_stimuli = params.get("stimuli", [])
                if isinstance(rep_stimuli, list):
                    known_stimuli.update(str(s) for s in rep_stimuli)

        if known_stimuli:
            unknown = sorted([k for k in attention.keys() if str(k) not in known_stimuli])
            if unknown:
                raise ValueError(f"attention keys not in known stimuli: {', '.join(unknown)}")

    @classmethod
    def _validate_phases(cls, exp: Mapping[str, Any]) -> None:
        phases = exp.get("phases")
        if not isinstance(phases, list):
            return
        for idx, phase in enumerate(phases):
            if not isinstance(phase, Mapping):
                raise ValueError(f"phase[{idx}] must be an object")
            params = phase.get("params", {})
            if not isinstance(params, Mapping):
                raise ValueError(f"phase[{idx}].params must be an object")

            leak = sorted([k for k in params.keys() if k in cls._LEAK_KEYS])
            if leak:
                raise ValueError(
                    f"phase[{idx}] params contain forbidden cross-concern keys: {', '.join(leak)}"
                )

            if "duration_s" in params and "dt_s" in params:
                duration = _as_float(params["duration_s"], "duration_s")
                dt = _as_float(params["dt_s"], "dt_s")
                if dt <= 0.0:
                    raise ValueError("dt_s must be > 0")
                if duration <= 0.0:
                    raise ValueError("duration_s must be > 0")
                if not _is_grid_aligned(duration, dt):
                    raise ValueError("dt_s must divide duration_s")

    @staticmethod
    def _validate_contexts(exp: Mapping[str, Any], rep: Any) -> None:
        known_contexts: set[str] = set()
        if isinstance(rep, Mapping):
            params = rep.get("params", {})
            if isinstance(params, Mapping):
                contexts = params.get("contexts")
                if isinstance(contexts, list):
                    known_contexts.update(str(c) for c in contexts)
        phases = exp.get("phases")
        if not isinstance(phases, list):
            return
        for idx, phase in enumerate(phases):
            if not isinstance(phase, Mapping):
                continue
            params = phase.get("params", {})
            if not isinstance(params, Mapping):
                continue
            ctx = params.get("context")
            if ctx is None:
                continue
            if known_contexts and str(ctx) not in known_contexts:
                raise ValueError(
                    f"phase[{idx}] context '{ctx}' not declared in representation contexts"
                )

