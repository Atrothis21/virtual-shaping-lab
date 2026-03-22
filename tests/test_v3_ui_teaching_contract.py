from __future__ import annotations

from ui.contracts.operator_registry import get_operator
from ui.contracts.preset_detail_contract import build_preset_detail_contract


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
