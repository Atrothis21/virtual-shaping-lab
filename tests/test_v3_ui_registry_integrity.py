from __future__ import annotations

import copy

import pytest

from ui.contracts.registry_integrity import (
    UIRegistryIntegrityError,
    load_ui_registries,
    validate_ui_registry_integrity,
)


def test_ui_registry_integrity_load_smoke():
    payload = load_ui_registries()
    assert set(payload.keys()) == {
        "trialstate_registry",
        "operator_registry",
        "dependent_variable_registry",
        "preset_registry",
    }
    assert payload["trialstate_registry"]["version"]
    assert payload["operator_registry"]["version"]
    assert payload["dependent_variable_registry"]["version"]
    assert payload["preset_registry"]["version"]


def test_ui_registry_integrity_rejects_invalid_operator_registry_cross_ref():
    registries = load_ui_registries()
    broken = copy.deepcopy(registries)
    broken["operator_registry"]["operators"]["w"]["runtime"]["writes_trialstate"].append("not_a_real_field")
    with pytest.raises(UIRegistryIntegrityError, match="operator_registry invalid"):
        validate_ui_registry_integrity(broken)

