"""Plan access compatibility adapters (typed-first, legacy-fallback)."""

from __future__ import annotations

import warnings
from typing import Any

from experiment.domain.types import ExperimentPlan


def get_typed_program_spec(plan: ExperimentPlan):
    """Return typed ProgramSpec from plan, synthesizing when necessary."""
    return plan.as_typed_program_spec()


def get_typed_agent_spec(plan: ExperimentPlan):
    """Return typed AgentSpec from plan, synthesizing when necessary."""
    return plan.as_typed_agent_spec()


def get_typed_runtime_spec(plan: ExperimentPlan):
    """Return typed RuntimeSpec from plan, synthesizing when necessary."""
    return plan.as_typed_runtime_spec()


def get_typed_analysis_spec(plan: ExperimentPlan):
    """Return typed AnalysisSpec from plan, synthesizing when necessary."""
    return plan.as_typed_analysis_spec()


def get_typed_experiment_spec(plan: ExperimentPlan):
    """Return typed ExperimentSpec from plan, synthesizing when necessary."""
    return plan.as_typed_experiment_spec()


def get_runtime_settings(plan: ExperimentPlan) -> dict[str, Any]:
    """
    Runtime settings accessor.

    Typed-first source:
    - plan.as_typed_runtime_spec().runtime
    """
    typed_runtime = plan.as_typed_runtime_spec()
    runtime = getattr(typed_runtime, "runtime", {}) or {}
    return dict(runtime)


def get_runtime_composed_parameters(plan: ExperimentPlan) -> dict[str, Any] | None:
    """
    Composed-parameters accessor.

    Source order:
    1) typed runtime spec (`typed_runtime_spec.composed_parameters`)
    2) runtime_spec dict (`plan.runtime_spec['composed_parameters']`)
    3) legacy plan.settings fallback (deprecated)
    """
    typed_runtime = plan.as_typed_runtime_spec()
    composed = dict(getattr(typed_runtime, "composed_parameters", {}) or {})
    if composed:
        return composed

    runtime_spec = dict(plan.runtime_spec or {})
    composed_runtime = runtime_spec.get("composed_parameters")
    if isinstance(composed_runtime, dict) and composed_runtime:
        return dict(composed_runtime)

    legacy_settings = dict(plan.settings or {})
    composed_legacy = legacy_settings.get("composed_parameters")
    if isinstance(composed_legacy, dict) and composed_legacy:
        warnings.warn(
            "Using legacy plan.settings['composed_parameters'] is deprecated; "
            "migrate runtime consumers to typed/runtime_spec plan fields.",
            DeprecationWarning,
            stacklevel=2,
        )
        return dict(composed_legacy)
    return None

