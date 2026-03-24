from __future__ import annotations

import copy

import pytest

from ui.contracts.preset_registry import (
    PRESET_REGISTRY,
    PresetRegistryValidationError,
    get_preset,
    get_preset_registry,
    list_preset_ids,
    validate_preset_registry,
)


def test_preset_registry_load_and_acquisition_exists():
    payload = get_preset_registry()
    assert payload["version"]
    presets = payload["presets"]
    assert "acquisition" in presets
    acquisition = presets["acquisition"]
    assert acquisition["id"] == "acquisition"
    assert acquisition["results_contract"]["primary_dependent_variables"]


def test_preset_registry_id_list_sorted_and_stable():
    ids = list_preset_ids()
    assert isinstance(ids, tuple)
    assert list(ids) == sorted(ids)
    assert "acquisition" in ids


def test_preset_registry_get_preset_success_and_failure():
    preset = get_preset("acquisition")
    assert preset["id"] == "acquisition"
    with pytest.raises(KeyError):
        get_preset("not_real")


def test_preset_registry_rejects_unknown_operator_reference():
    payload = copy.deepcopy(PRESET_REGISTRY)
    payload["presets"]["acquisition"]["registry_bindings"]["operators"].append("unknown_operator")
    with pytest.raises(PresetRegistryValidationError, match="references unknown operator id"):
        validate_preset_registry(payload)


def test_preset_registry_rejects_unknown_results_variable_reference():
    payload = copy.deepcopy(PRESET_REGISTRY)
    payload["presets"]["acquisition"]["results_contract"]["graph_priority"].append("unknown_variable")
    with pytest.raises(PresetRegistryValidationError, match="references unknown dependent variable id"):
        validate_preset_registry(payload)


def test_preset_registry_rejects_undeclared_results_variable():
    payload = copy.deepcopy(PRESET_REGISTRY)
    payload["presets"]["acquisition"]["registry_bindings"]["dependent_variables"] = [
        "associative_strength",
    ]
    with pytest.raises(PresetRegistryValidationError, match="contains undeclared dependent variable"):
        validate_preset_registry(payload)


def test_preset_registry_rejects_preset_id_mismatch():
    payload = copy.deepcopy(PRESET_REGISTRY)
    payload["presets"]["acquisition"]["id"] = "acq"
    with pytest.raises(PresetRegistryValidationError, match="id must match preset key"):
        validate_preset_registry(payload)


def test_preset_registry_rejects_non_registry_selectable_universe_source():
    payload = copy.deepcopy(PRESET_REGISTRY)
    payload["presets"]["acquisition"]["basis_definition"]["selectable_universe_source"] = "hand_authored"
    with pytest.raises(PresetRegistryValidationError, match="selectable_universe_source"):
        validate_preset_registry(payload)

