"""Build immutable experiment plans from normalized config objects."""

from __future__ import annotations

from typing import Any

from experiment.config import ExperimentConfig
from experiment.domain.types import ExperimentPlan


def build_experiment_plan(config: ExperimentConfig) -> ExperimentPlan:
    """Convert an ExperimentConfig into a declarative ExperimentPlan."""
    units: list[dict[str, Any]] = []
    for phase in config.phases:
        units.append(
            {
                "name": phase.name,
                "protocol": phase.protocol,
                "stimuli": phase.stimuli,
                "params": dict(phase.params or {}),
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
        "representation": config.representation,
        "policy": config.policy,
        "stimuli": list(config.stimuli),
        "salience": dict(config.salience),
        "attention": dict(config.attention),
        "context_inference": dict(config.context_inference),
        "report_preset": config.report_preset,
    }

    return ExperimentPlan(
        units=units,
        seed=seed,
        record_schema_version="v1",
        settings=settings,
    )

