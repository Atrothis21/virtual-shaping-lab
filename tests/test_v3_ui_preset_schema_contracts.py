from __future__ import annotations

import copy

import pytest

from ui.contracts.preset_registry import (
    PRESET_REGISTRY,
    PresetRegistryValidationError,
    get_preset,
    get_preset_registry,
    validate_preset_registry,
)
from ui.contracts.registry_integrity import load_ui_registries


def test_v3_10_5_entry_criteria_v3_10_0_registries_are_available():
    registries = load_ui_registries()
    assert "trialstate_registry" in registries
    assert "operator_registry" in registries
    assert "dependent_variable_registry" in registries
    assert "preset_registry" in registries
    assert "acquisition" in registries["preset_registry"]["presets"]


def test_acquisition_preset_schema_has_ui_locking_and_editability_sections():
    preset = get_preset("acquisition")
    ui_contract = preset["ui_contract"]
    assert set(("layers", "locking", "editability")).issubset(ui_contract.keys())
    assert set(("overview", "phases", "operators", "math")).issubset(ui_contract["layers"].keys())
    assert set(("protocol_locked", "phase_structure_locked", "operators_read_only")).issubset(
        ui_contract["locking"].keys()
    )
    assert set(("allowed_parameters", "locked_parameters")).issubset(ui_contract["editability"].keys())


def test_acquisition_preset_invariant_one_phase_and_acquisition_protocol():
    preset = get_preset("acquisition")
    phases = preset["template"]["experiment"]["program"]["phases"]
    assert len(phases) == 1
    assert phases[0]["protocol"] == "acquisition"


def test_acquisition_preset_invariant_required_operators_present():
    preset = get_preset("acquisition")
    operators = set(preset["registry_bindings"]["operators"])
    assert {"phi", "p", "delta", "w", "m"}.issubset(operators)


def test_acquisition_preset_rejects_missing_required_operator():
    payload = copy.deepcopy(PRESET_REGISTRY)
    payload["presets"]["acquisition"]["registry_bindings"]["operators"] = ["phi", "p", "delta", "w"]
    with pytest.raises(PresetRegistryValidationError, match="missing required operators"):
        validate_preset_registry(payload)


def test_acquisition_preset_rejects_non_acquisition_protocol():
    payload = copy.deepcopy(PRESET_REGISTRY)
    payload["presets"]["acquisition"]["template"]["experiment"]["program"]["phases"][0]["protocol"] = "extinction"
    with pytest.raises(PresetRegistryValidationError, match="phase protocol must be 'acquisition'"):
        validate_preset_registry(payload)


def test_acquisition_preset_rejects_multi_phase_template():
    payload = copy.deepcopy(PRESET_REGISTRY)
    payload["presets"]["acquisition"]["template"]["experiment"]["program"]["phases"].append(
        {
            "name": "Extra",
            "protocol": "acquisition",
            "stimuli": {"cs_plus": ["tone"]},
            "params": {"n_trials": 5},
        }
    )
    with pytest.raises(PresetRegistryValidationError, match="expected exactly one phase"):
        validate_preset_registry(payload)


def test_acquisition_preset_rejects_overlapping_allowed_and_locked_params():
    payload = copy.deepcopy(PRESET_REGISTRY)
    payload["presets"]["acquisition"]["ui_contract"]["editability"]["allowed_parameters"].append(
        "experiment.program.phases"
    )
    with pytest.raises(PresetRegistryValidationError, match="overlapping allowed/locked"):
        validate_preset_registry(payload)


def test_acquisition_preset_registry_load_smoke():
    payload = get_preset_registry()
    assert payload["version"]
    assert "acquisition" in payload["presets"]

