from __future__ import annotations

import copy

from experiment.assemble import _plan_to_config
from experiment.domain.types import ExperimentPlan
from ui.contracts.operator_plan_materialization import compile_and_materialize_operator_plan
from ui.contracts.operator_selection_compiler import compile_operator_selection_artifact
from ui.contracts.operator_subset_contract import PRESET_DEFINITION_TEMPLATE


def _basis_payload(protocol_family: str = "acquisition") -> tuple[dict, dict]:
    preset = copy.deepcopy(PRESET_DEFINITION_TEMPLATE)
    preset["id"] = f"rw_{protocol_family}"
    compiled = compile_operator_selection_artifact(preset)
    materialized = compile_and_materialize_operator_plan(
        preset,
        protocol_family=protocol_family,
        stimuli_catalog=["tone", "noise"],
    )
    return compiled, materialized


def test_experiment_plan_basis_typed_surfaces_roundtrip():
    compiled, materialized = _basis_payload("acquisition")
    plan = ExperimentPlan(
        units=[],
        basis_compile_artifact=compiled,
        basis_materialized_sections=materialized,
        canonical_payload={"experiment": {}, "report": {"preset": "acquisition"}},
    )
    blob = plan.to_dict()
    assert blob["basis_compile_artifact"] == compiled
    assert blob["basis_materialized_sections"] == materialized

    rebuilt = ExperimentPlan.from_dict(blob)
    assert rebuilt.basis_compile() == compiled
    assert rebuilt.basis_materialized() == materialized


def test_basis_adapter_prefers_basis_materialized_sections_over_legacy_fields():
    _compiled, materialized = _basis_payload("acquisition")
    plan = ExperimentPlan(
        units=[
            {
                "name": "Legacy Extinction",
                "protocol": "extinction",
                "stimuli": {"cs_plus": ["noise"]},
                "params": {"n_trials": 1},
            }
        ],
        program_spec={
            "phases": [
                {
                    "name": "Legacy Differential",
                    "protocol": "differential_acquisition",
                    "stimuli": {"cs_plus": ["noise"], "cs_minus": ["tone"]},
                    "params": {"n_trials": 1},
                }
            ]
        },
        agent_spec={
            "agent": "legacy_agent",
            "representation": {"name": "legacy_rep", "params": {"stimuli": ["noise"]}},
            "learning": {"rule": "legacy_rule", "params": {}},
        },
        runtime_spec={"resolved_plan": True},
        basis_materialized_sections=materialized,
        canonical_payload={"experiment": {}, "report": {"preset": "acquisition"}},
    )
    config = _plan_to_config(plan)
    assert config.phases[0].protocol == "acquisition"
    assert config.representation["name"] == "vector_elemental"
    assert config.learner == "rescorla_wagner"


def test_basis_adapter_ignores_legacy_phase_source_for_covered_presets():
    _compiled, materialized = _basis_payload("acquisition")
    plan = ExperimentPlan(
        units=[
            {
                "name": "Legacy Invalid",
                "protocol": "this_should_not_be_used",
                "stimuli": {"cs_plus": ["noise"]},
                "params": {"n_trials": 1},
            }
        ],
        program_spec={
            "phases": [
                {
                    "name": "Legacy Also Invalid",
                    "protocol": "still_should_not_be_used",
                    "stimuli": {"cs_plus": ["noise"]},
                    "params": {"n_trials": 1},
                }
            ]
        },
        agent_spec={
            "agent": "legacy_agent",
            "representation": {"name": "legacy_rep", "params": {"stimuli": ["noise"]}},
            "learning": {"rule": "legacy_rule", "params": {}},
        },
        runtime_spec={"resolved_plan": True},
        basis_materialized_sections=materialized,
        canonical_payload={"experiment": {}, "report": {"preset": "acquisition"}},
    )
    config = _plan_to_config(plan)
    assert len(config.phases) == 1
    assert config.phases[0].protocol == "acquisition"
    assert config.phases[0].name == "Acquisition"


def test_basis_adapter_falls_back_to_legacy_when_basis_sections_absent():
    plan = ExperimentPlan(
        units=[
            {
                "name": "Legacy Acquisition",
                "protocol": "acquisition",
                "stimuli": {"cs_plus": ["tone"]},
                "params": {"n_trials": 1},
            }
        ],
        agent_spec={
            "agent": "classical_agent",
            "representation": {"name": "vector_elemental", "params": {"stimuli": ["tone"]}},
            "learning": {"rule": "rescorla_wagner", "params": {}},
            "policy": None,
        },
        runtime_spec={"resolved_plan": True},
        canonical_payload={"experiment": {}, "report": {"preset": "acquisition"}},
    )
    config = _plan_to_config(plan)
    assert config.phases[0].protocol == "acquisition"
    assert config.representation["name"] == "vector_elemental"
    assert config.learner == "rescorla_wagner"


def test_plan_hash_stability_ignores_basis_metadata():
    base_payload = {"experiment": {"program": {"phases": []}}, "report": {"preset": "acquisition"}}
    compiled, materialized = _basis_payload("acquisition")
    p1 = ExperimentPlan(
        units=[],
        canonical_payload=base_payload,
        basis_compile_artifact={},
        basis_materialized_sections={},
    )
    p2 = ExperimentPlan(
        units=[],
        canonical_payload=copy.deepcopy(base_payload),
        basis_compile_artifact=compiled,
        basis_materialized_sections=materialized,
    )
    assert p1.stable_hash() == p2.stable_hash()
