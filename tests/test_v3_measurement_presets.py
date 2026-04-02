from __future__ import annotations

import pytest

from virtual_shaping_lab.vsl.measurement import (
    MEASUREMENT_PRESETS,
    expand_measurement_preset,
    measurement_preset_aliases,
    measurement_preset_families,
    measurement_preset_hash,
    measurement_preset_names,
    measurement_preset_payload,
    measurement_preset_registry,
)


def test_v3_measurement_preset_registry_is_deterministic():
    names = measurement_preset_names()
    registry = measurement_preset_registry()
    assert names == sorted(MEASUREMENT_PRESETS.keys())
    assert set(registry.keys()) == set(names)


def test_v3_measurement_preset_aliases_and_families_have_entries():
    aliases = measurement_preset_aliases()
    families = measurement_preset_families()
    assert "learning" in aliases
    assert "classical" in families


def test_v3_measurement_preset_payload_and_hash_are_stable():
    payload = measurement_preset_payload("learning")
    assert payload["preset_name"] == "learning_curve_basic"
    hashes = [measurement_preset_hash("learning") for _ in range(20)]
    assert len(set(hashes)) == 1


def test_v3_measurement_preset_expand_unknown_raises():
    with pytest.raises(ValueError, match="MEAS_E_UNKNOWN_PRESET"):
        expand_measurement_preset("unknown_preset")
