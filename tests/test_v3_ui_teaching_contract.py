from __future__ import annotations

import copy

from ui.contracts.operator_registry import get_operator
from ui.contracts.preset_detail_contract import build_preset_detail_contract
import ui.contracts.preset_detail_contract as preset_detail_contract


def test_v3_teaching_contract_acquisition_layers_present():
    detail = build_preset_detail_contract("acquisition")
    assert detail["layers"]["overview"] is True
    assert detail["layers"]["phases"] is True
    assert detail["layers"]["operators"] is True
    assert detail["layers"]["math"] is True
    assert detail["overview"]["phase_summary"] == "acquisition"


def test_v3_teaching_contract_acquisition_phase_block_read_only():
    detail = build_preset_detail_contract("acquisition")
    phases = detail["phases"]
    assert len(phases) == 1
    phase = phases[0]
    assert phase["protocol"] == "acquisition"
    assert phase["read_only"] is True
    assert "n_trials" in phase["parameter_keys"]
    assert "cs_plus" in phase["stimulus_keys"]


def test_v3_teaching_contract_acquisition_operator_surface_registry_driven_and_read_only():
    detail = build_preset_detail_contract("acquisition")
    assert detail["operator_surface_read_only"] is True
    operators = detail["operators"]
    assert operators

    expected_ids = {"phi", "p", "delta", "w", "m"}
    assert expected_ids.issubset({op["id"] for op in operators})
    assert all(op["read_only"] is True for op in operators)

    stage_indices = [op["stage_index"] for op in operators]
    assert stage_indices == sorted(stage_indices)

    for rendered in operators:
        canonical = get_operator(rendered["id"])
        assert rendered["stage_index"] == canonical["stage_index"]
        assert rendered["reads_trialstate"] == canonical["runtime"]["reads_trialstate"]
        assert rendered["writes_trialstate"] == canonical["runtime"]["writes_trialstate"]


def test_v3_teaching_contract_prefers_basis_subset_over_hand_authored_operator_strings(monkeypatch):
    preset = {
        "id": "acquisition",
        "label": "Acquisition",
        "description": "test preset",
        "protocol_family": "acquisition",
        "template": {
            "experiment": {
                "program": {"phases": [{"name": "Acquisition", "protocol": "acquisition", "stimuli": {}, "params": {}}]}
            }
        },
        "ui_contract": {"layers": {"overview": True, "phases": True, "operators": True, "math": True}},
        "basis_definition": {
            "operator_subset": {"phi": "elemental", "p": "state_value", "delta": "rw_error", "w": "rescorla_wagner", "m": ["trial_log"]},
        },
        "registry_bindings": {
            "operators": ["m"],  # Intentionally wrong ordering/content; basis subset should win.
        },
    }
    monkeypatch.setattr(preset_detail_contract, "get_preset", lambda _preset_id: copy.deepcopy(preset))
    detail = preset_detail_contract.build_preset_detail_contract("acquisition")
    observed = [entry["id"] for entry in detail["operators"]]
    assert {"phi", "p", "delta", "w", "m"}.issubset(set(observed))
