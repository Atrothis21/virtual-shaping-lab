"""Public experiment facade.

Stable high-level entrypoints for plan build/validation and execution.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional

from experiment.assemble import assemble_experiment
from experiment.config import ExperimentConfig
from experiment.domain.types import ExperimentPlan
from experiment.phenomena.catalog import available_phenomena, get_phenomenon
from experiment.parameters import validate_composed_parameter_ownership
from experiment.runner import Runner


def build_plan(payload: dict[str, Any]) -> ExperimentPlan:
    """Build a resolved ExperimentPlan from payload."""
    return ExperimentConfig.plan_from_payload(payload)


def validate_plan(plan: ExperimentPlan) -> ExperimentPlan:
    """Validate plan-level ownership constraints and return the same plan."""
    settings = dict(plan.settings or {})
    composed = settings.get("composed_parameters")
    if composed:
        validate_composed_parameter_ownership(composed)
    return plan


def assemble_from_plan(plan: ExperimentPlan):
    """Assemble runtime units, agent, and representation from a plan."""
    validate_plan(plan)
    return assemble_experiment(plan)


@dataclass
class ExecutionResult:
    records: list[dict[str, Any]]
    unit_records: list[list[dict[str, Any]]]
    runtime_units: list[Any]
    agent: Any
    representation: Any


def run_from_plan(
    plan: ExperimentPlan,
    *,
    seed: Optional[int] = None,
    context: Any = None,
    settings: Optional[dict[str, Any]] = None,
    sink: Any = None,
    hooks: Any = None,
) -> ExecutionResult:
    """Assemble and execute all runtime units declared by the plan."""
    runtime_units, agent, representation = assemble_from_plan(plan)
    runner_settings = dict(plan.settings or {})
    if settings:
        runner_settings.update(settings)

    all_records: list[dict[str, Any]] = []
    unit_records: list[list[dict[str, Any]]] = []
    for unit in runtime_units:
        records_for_unit = Runner(
            unit,
            seed=seed,
            context=context,
            settings=runner_settings,
            sink=sink,
            hooks=hooks,
        ).run()
        unit_records.append(records_for_unit)
        all_records.extend(records_for_unit)

    return ExecutionResult(
        records=all_records,
        unit_records=unit_records,
        runtime_units=runtime_units,
        agent=agent,
        representation=representation,
    )


def list_phenomena() -> dict[str, dict[str, Any]]:
    """Return typed phenomena discovery payload for UI/API callers."""
    result: dict[str, dict[str, Any]] = {}
    for key in available_phenomena():
        spec = get_phenomenon(key)
        result[key] = {
            "name": spec.name,
            "description": spec.description,
            "protocol_key": spec.protocol_key,
            "expected_signatures": list(spec.expected_signatures),
            "default_template_key": spec.default_template_key,
            "recommended_presets": [dict(p) for p in spec.recommended_presets],
        }
    return result
