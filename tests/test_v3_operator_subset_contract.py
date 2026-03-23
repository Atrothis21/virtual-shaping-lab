from __future__ import annotations

import copy

import pytest

from ui.contracts.operator_subset_contract import (
    PRESET_DEFINITION_TEMPLATE,
    OperatorSubsetContractError,
    build_registry_generated_ui_universe,
    get_preset_definition_template,
    validate_preset_definition,
    validate_registry_generated_ui_universe,
)


def test_preset_definition_template_is_valid():
    payload = get_preset_definition_template()
    assert payload["id"] == "rw_acquisition"
    assert "operator_subset" in payload


def test_preset_definition_rejects_missing_required_operator_slot():
    payload = copy.deepcopy(PRESET_DEFINITION_TEMPLATE)
    del payload["operator_subset"]["omega"]
    with pytest.raises(OperatorSubsetContractError, match="missing required slots"):
        validate_preset_definition(payload)


def test_preset_definition_rejects_unknown_slot():
    payload = copy.deepcopy(PRESET_DEFINITION_TEMPLATE)
    payload["operator_subset"]["not_a_slot"] = "whatever"
    with pytest.raises(OperatorSubsetContractError, match="unknown slots"):
        validate_preset_definition(payload)


def test_preset_definition_rejects_invalid_selection_for_slot():
    payload = copy.deepcopy(PRESET_DEFINITION_TEMPLATE)
    payload["operator_subset"]["delta"] = "not_real"
    with pytest.raises(OperatorSubsetContractError, match="must be one of"):
        validate_preset_definition(payload)


def test_preset_definition_rejects_locked_optional_overlap():
    payload = copy.deepcopy(PRESET_DEFINITION_TEMPLATE)
    payload["optional"].append("w")
    with pytest.raises(OperatorSubsetContractError, match="overlap"):
        validate_preset_definition(payload)


def test_preset_definition_rejects_defaults_on_locked_slots():
    payload = copy.deepcopy(PRESET_DEFINITION_TEMPLATE)
    payload["defaults"]["w"] = "rescorla_wagner"
    with pytest.raises(OperatorSubsetContractError, match="cannot include locked slots"):
        validate_preset_definition(payload)


def test_registry_generated_ui_universe_passes_when_unmodified():
    universe = build_registry_generated_ui_universe()
    validated = validate_registry_generated_ui_universe(universe)
    assert set(validated.keys()) == set(universe.keys())


def test_registry_generated_ui_universe_rejects_hand_authored_drift():
    universe = build_registry_generated_ui_universe()
    hacked = {k: list(v) for k, v in universe.items()}
    hacked["phi"] = hacked["phi"] + ["hand_authored_option"]
    with pytest.raises(OperatorSubsetContractError, match="must be registry-generated"):
        validate_registry_generated_ui_universe(hacked)

