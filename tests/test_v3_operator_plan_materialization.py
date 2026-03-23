from __future__ import annotations

import copy

from ui.contracts.operator_plan_materialization import (
    compile_and_materialize_operator_plan,
    materialize_compiled_operator_plan_sections,
)
from ui.contracts.operator_selection_compiler import compile_operator_selection_artifact
from ui.contracts.operator_subset_contract import PRESET_DEFINITION_TEMPLATE


def _base_preset() -> dict:
    return copy.deepcopy(PRESET_DEFINITION_TEMPLATE)


def test_materialized_plan_shape_for_acquisition():
    compiled = compile_operator_selection_artifact(_base_preset())
    payload = materialize_compiled_operator_plan_sections(
        compiled,
        protocol_family="acquisition",
        stimuli_catalog=["tone", "noise"],
    )
    assert set(payload.keys()) == {"experiment"}
    assert set(payload["experiment"].keys()) == {"agent", "runtime", "program"}
    assert set(payload["experiment"]["agent"].keys()) == {"name", "representation", "learning", "policy"}
    assert set(payload["experiment"]["runtime"].keys()) == {"environment", "measurement", "operator_routes"}
    assert set(payload["experiment"]["program"].keys()) == {"phases"}


def test_materialization_emits_no_undeclared_top_level_fields():
    payload = compile_and_materialize_operator_plan(
        _base_preset(),
        protocol_family="acquisition",
    )
    assert set(payload.keys()) == {"experiment", "materialization"}
    assert set(payload["materialization"].keys()) == {
        "version",
        "protocol_family",
        "compiled_hash",
        "materialized_hash",
    }


def test_materialization_conforms_for_acquisition_extinction_and_differential():
    for protocol_family in ("acquisition", "extinction", "differential_acquisition"):
        payload = compile_and_materialize_operator_plan(
            _base_preset(),
            protocol_family=protocol_family,
            stimuli_catalog=["tone", "noise"],
        )
        phases = payload["experiment"]["program"]["phases"]
        assert len(phases) == 1
        assert phases[0]["protocol"] == protocol_family
        assert "operator_attachments" in phases[0]
        assert "route_map" in phases[0]["operator_attachments"]


def test_materialization_route_snapshot_ui_selection_to_builder_family():
    payload = compile_and_materialize_operator_plan(
        _base_preset(),
        protocol_family="acquisition",
    )
    routes = payload["experiment"]["runtime"]["operator_routes"]
    assert routes["phi"] == [{"selection_id": "elemental", "internal_builder_family": "representation"}]
    assert routes["p"] == [{"selection_id": "state_value", "internal_builder_family": "learner"}]
    assert routes["delta"] == [{"selection_id": "rw_error", "internal_builder_family": "learner"}]
    assert routes["w"] == [{"selection_id": "rescorla_wagner", "internal_builder_family": "learner"}]
    assert routes["omega"] == [
        {"selection_id": "classical_contingency", "internal_builder_family": "environment_protocol"}
    ]

