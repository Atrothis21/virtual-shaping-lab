from __future__ import annotations

import warnings

from experiment.domain.types import ExperimentPlan
from experiment.plan_access import (
    get_runtime_composed_parameters,
    get_runtime_settings,
    get_typed_experiment_spec,
)


def _base_plan() -> ExperimentPlan:
    return ExperimentPlan(
        units=[],
        program_spec={"phases": []},
        agent_spec={
            "agent": "classical_agent",
            "representation": {"name": "vector_elemental", "params": {"stimuli": ["tone"]}},
            "learning": {"rule": "rescorla_wagner", "params": {}, "attention": {"initial": {}, "config": {"name": "none", "params": {}}}},
            "policy": None,
        },
        runtime_spec={"runtime": {"debug": False}, "composed_parameters": {"learner": {"algorithm": "rescorla_wagner"}}},
        analysis_spec={"report_preset": "acquisition"},
        canonical_payload={"experiment": {"program": {"phases": []}, "agent": {}, "runtime": {}}, "report": {"preset": "acquisition"}},
        settings={},
    )


def test_plan_access_prefers_runtime_spec_and_typed_paths():
    plan = _base_plan()
    runtime = get_runtime_settings(plan)
    composed = get_runtime_composed_parameters(plan)
    typed = get_typed_experiment_spec(plan)

    assert runtime["debug"] is False
    assert composed == {"learner": {"algorithm": "rescorla_wagner"}}
    assert typed.analysis.report_preset == "acquisition"


def test_plan_access_warns_on_legacy_settings_fallback():
    plan = _base_plan()
    plan = ExperimentPlan(
        units=plan.units,
        program_spec=plan.program_spec,
        agent_spec=plan.agent_spec,
        runtime_spec={"runtime": {"debug": False}},
        analysis_spec=plan.analysis_spec,
        canonical_payload=plan.canonical_payload,
        settings={"composed_parameters": {"learner": {"algorithm": "rescorla_wagner"}}},
    )

    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        composed = get_runtime_composed_parameters(plan)

    assert composed == {"learner": {"algorithm": "rescorla_wagner"}}
    assert any(issubclass(w.category, DeprecationWarning) for w in caught)

