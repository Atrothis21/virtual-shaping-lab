from __future__ import annotations

import copy

import pytest

from ui.contracts.preset_registry import PRESET_REGISTRY
from ui.contracts.preset_run_flow import (
    PresetRunFlowContractError,
    build_preset_run_flow_contract,
    resolve_results_contract_from_preset,
    validate_preset_results_priority,
)


def test_acquisition_end_to_end_flow_contract_library_detail_run_results():
    flow = build_preset_run_flow_contract(
        "acquisition",
        edits={"experiment.program.phases[0].params.n_trials": 12},
    )
    assert flow["preset_id"] == "acquisition"
    assert flow["flow"]["route_sequence"] == ["library", "detail", "run", "results"]
    assert flow["flow"]["run_action"]["from"] == "detail"
    assert flow["flow"]["run_action"]["to"] == "results"
    assert flow["flow"]["run_action"]["results_route"] == "/ui/results.html?preset=acquisition"
    assert flow["payload"]["report"]["preset"] == "acquisition"
    assert flow["payload"]["experiment"]["program"]["phases"][0]["params"]["n_trials"] == 12


def test_acquisition_results_contract_rejects_unknown_dependent_variable_id():
    payload = copy.deepcopy(PRESET_REGISTRY)
    payload["presets"]["acquisition"]["results_contract"]["graph_priority"].append("not_a_variable")

    with pytest.raises(PresetRunFlowContractError, match="unknown dependent-variable IDs"):
        resolve_results_contract_from_preset(payload["presets"]["acquisition"])


def test_acquisition_results_graph_priority_behavioral_learning_first():
    validate_preset_results_priority("acquisition")
    flow = build_preset_run_flow_contract("acquisition")
    first_two_categories = [entry["category"] for entry in flow["results_view"]["graph_priority"][:2]]
    assert all(category in {"behavioral", "learning"} for category in first_two_categories)
