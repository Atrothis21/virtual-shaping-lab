"""Build immutable experiment plans from normalized config objects."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from experiment.config import ExperimentConfig
from experiment.domain.types import ExperimentPlan


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

    settings = {
        "learner": config.learner,
        "agent": config.agent,
        "representation": _resolve_representation(config, inferred_phase_contexts),
        "policy": deepcopy(config.policy),
        "stimuli": list(config.stimuli),
        "salience": dict(config.salience),
        "attention": dict(config.attention),
        "context_inference": dict(config.context_inference),
        "report_preset": config.report_preset,
        "resolved_plan": True,
        "resolved_phase_contexts": inferred_phase_contexts,
    }

    return ExperimentPlan(
        units=units,
        seed=seed,
        record_schema_version="v1",
        settings=settings,
    )

