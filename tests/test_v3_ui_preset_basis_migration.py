from __future__ import annotations

from ui.contracts.preset_detail_contract import build_preset_detail_contract
from ui.contracts.preset_registry import get_preset_registry
from ui.contracts.operator_subset_contract import validate_preset_definition


CORE_PRESETS = ("acquisition", "extinction", "differential_acquisition")


def test_core_presets_include_basis_definitions():
    payload = get_preset_registry()
    for preset_id in CORE_PRESETS:
        preset = payload["presets"][preset_id]
        basis = preset["basis_definition"]
        assert basis["selectable_universe_source"] == "operator_basis_registry"
        validate_preset_definition(basis)


def test_teaching_detail_contract_for_core_presets_is_basis_and_registry_driven():
    for preset_id in CORE_PRESETS:
        detail = build_preset_detail_contract(preset_id)
        operator_ids = {entry["id"] for entry in detail["operators"]}
        assert {"phi", "p", "delta", "w", "m"}.issubset(operator_ids)
        assert all(entry["read_only"] is True for entry in detail["operators"])
