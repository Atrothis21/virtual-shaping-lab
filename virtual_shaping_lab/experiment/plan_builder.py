"""Build immutable experiment plans from normalized config objects."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from experiment.config import ExperimentConfig
from experiment.domain.types import ExperimentPlan
from experiment.parameters import ParameterComposer, parameters_to_dict
from virtual_shaping_lab.vsl.spec import (
    AgentSpec,
    AnalysisSpec,
    EnvironmentProgramSpec,
    ExperimentSpec,
    ProgramSpec,
    RuntimeSpec,
)
from virtual_shaping_lab.vsl.agent.learning import resolve_learner_spec


def _infer_phase_contexts(config: ExperimentConfig) -> list[str | None]:
    inference = getattr(config, "context_inference", {}) or {}
    if not inference.get("enabled"):
        return [None] * len(config.phases)

    max_contexts = int(inference.get("max_contexts", 3))
    max_contexts = max(1, min(3, max_contexts))
    labels = ["A", "B", "C"][:max_contexts]

    inferred: list[str | None] = []
    last_name = None
    idx = 0
    for phase in config.phases:
        if phase.name == last_name and inferred:
            inferred.append(inferred[-1])
            continue
        label = labels[idx] if idx < len(labels) else labels[-1]
        inferred.append(label)
        last_name = phase.name
        if idx < len(labels) - 1:
            idx += 1
    return inferred


def _resolve_representation(config: ExperimentConfig, inferred_phase_contexts: list[str | None]) -> dict[str, Any]:
    rep = config.representation
    if isinstance(rep, dict):
        rep_name = rep.get("name")
        rep_params = dict(rep.get("params", {}) or {})
    else:
        rep_name = rep
        rep_params = {}

    if config.stimuli:
        rep_params.setdefault("stimuli", list(config.stimuli))
    if config.salience:
        rep_params.setdefault("salience", dict(config.salience))

    contexts = set(rep_params.get("contexts", []))
    for phase in config.phases:
        for key, value in (phase.params or {}).items():
            if key == "context" and value:
                contexts.add(value)
            if key.startswith("context_") and value:
                contexts.add(value)
    contexts.update(label for label in inferred_phase_contexts if label is not None)
    if not contexts:
        contexts.add("A")
    rep_params["contexts"] = sorted(contexts)
    return {"name": rep_name, "params": rep_params}


def build_experiment_plan(config: ExperimentConfig) -> ExperimentPlan:
    """Convert an ExperimentConfig into a declarative ExperimentPlan."""
    inferred_phase_contexts = _infer_phase_contexts(config)
    units: list[dict[str, Any]] = []
    for idx, phase in enumerate(config.phases):
        params = deepcopy(phase.params or {})
        inferred_ctx = inferred_phase_contexts[idx] if idx < len(inferred_phase_contexts) else None
        if inferred_ctx and not params.get("context"):
            params["context"] = inferred_ctx
            params["context_source"] = "inferred"
        units.append(
            {
                "name": phase.name,
                "protocol": phase.protocol,
                "stimuli": deepcopy(phase.stimuli),
                "params": params,
            }
        )

    seed = None
    if config.phases:
        first_params = config.phases[0].params or {}
        if "rng_seed" in first_params:
            seed = first_params.get("rng_seed")

    learning_config = {
        "rule": config.learner,
        "params": {},
        "attention": {
            "initial": dict(config.attention),
            "config": dict(config.attention_config),
        },
    }
    learner_spec = resolve_learner_spec(
        learner_rule=config.learner,
        policy_config=config.policy,
        learning_config=learning_config,
        metadata={"boundary": "spec_build"},
    )

    settings = {
        "learner": config.learner,
        "agent": config.agent,
        "representation": _resolve_representation(config, inferred_phase_contexts),
        "policy": deepcopy(config.policy),
        "stimuli": list(config.stimuli),
        "salience": dict(config.salience),
        "attention": dict(config.attention),
        "attention_config": dict(config.attention_config),
        "context_inference": dict(config.context_inference),
        "runtime": dict(config.runtime),
        "report_preset": config.report_preset,
        "resolved_plan": True,
        "resolved_phase_contexts": inferred_phase_contexts,
        "composed_parameters": _compose_parameter_settings(config),
        "learner_spec": learner_spec.to_dict(),
        "learner_spec_hash": learner_spec.stable_hash(),
    }
    canonical_payload = _build_canonical_payload_settings(config)

    program_spec = {
        "phases": deepcopy(units),
        "resolved_phase_contexts": list(inferred_phase_contexts),
    }
    agent_spec = {
        "agent": config.agent,
        "representation": _resolve_representation(config, inferred_phase_contexts),
        "learning": {
            **learning_config,
            "learner_spec": learner_spec.to_dict(),
        },
        "policy": deepcopy(config.policy),
        "stimuli": list(config.stimuli),
        "salience": dict(config.salience),
        "attention": dict(config.attention),
        "attention_config": dict(config.attention_config),
    }
    runtime_spec = {
        "runtime": dict(config.runtime),
        "context_inference": dict(config.context_inference),
        "resolved_plan": True,
        "composed_parameters": deepcopy(settings["composed_parameters"]),
    }
    analysis_spec = {
        "report_preset": config.report_preset,
    }

    typed_program_spec = ProgramSpec.from_dict(program_spec)
    typed_agent_spec = AgentSpec.from_dict(agent_spec)
    typed_runtime_spec = RuntimeSpec.from_dict(runtime_spec)
    typed_analysis_spec = AnalysisSpec.from_dict(analysis_spec)
    typed_environment_program_spec = EnvironmentProgramSpec.from_dict({})
    typed_experiment_spec = ExperimentSpec(
        program=typed_program_spec,
        agent=typed_agent_spec,
        runtime=typed_runtime_spec,
        analysis=typed_analysis_spec,
        environment_program=typed_environment_program_spec,
        canonical_payload=dict(canonical_payload or {}),
    )

    return ExperimentPlan(
        units=units,
        program_spec=program_spec,
        agent_spec=agent_spec,
        runtime_spec=runtime_spec,
        analysis_spec=analysis_spec,
        canonical_payload=canonical_payload,
        seed=seed,
        record_schema_version="v1",
        settings=settings,
        typed_program_spec=typed_program_spec,
        typed_agent_spec=typed_agent_spec,
        typed_runtime_spec=typed_runtime_spec,
        typed_analysis_spec=typed_analysis_spec,
        typed_environment_program_spec=typed_environment_program_spec,
        typed_experiment_spec=typed_experiment_spec,
    )


def _compose_parameter_settings(config: ExperimentConfig) -> dict[str, Any]:
    payload = _build_canonical_payload_settings(config)
    # Compose from canonical payload through the standard normalization path so
    # plan.settings matches ParameterComposer.compose(plan.canonical_payload).
    composed = ParameterComposer.compose(payload)
    return parameters_to_dict(composed)


def _build_canonical_payload_settings(config: ExperimentConfig) -> dict[str, Any]:
    phases = []
    for i, phase in enumerate(config.phases):
        params = deepcopy(phase.params or {})
        trials = int(params.get("n_trials", 1))
        phases.append(
            {
                "name": phase.name or f"Phase {i}",
                "protocol": phase.protocol,
                "stimuli": deepcopy(phase.stimuli),
                "params": params,
                "trials": trials,
            }
        )
    runtime = dict(config.runtime or {})
    if isinstance(config.context_inference, dict):
        runtime.setdefault("context_inference", dict(config.context_inference))
    return {
        "experiment": {
            "program": {"phases": phases},
            "agent": {
                "name": config.agent,
                "representation": _resolve_representation(config, _infer_phase_contexts(config)),
                "learning": {
                    "rule": config.learner,
                    "params": {},
                    "attention": {
                        "config": dict(config.attention_config or {}),
                        "initial": dict(config.attention or {}),
                    },
                },
                "policy": deepcopy(config.policy),
            },
            "runtime": runtime,
        },
        "report": {"preset": config.report_preset},
    }

