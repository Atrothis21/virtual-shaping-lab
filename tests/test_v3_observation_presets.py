from __future__ import annotations

import pytest

from virtual_shaping_lab.vsl.agent.observation import (
    OBSERVATION_PRESET_FAMILIES,
    OBSERVATION_PRESETS,
    PRESET_VERSION,
    ObservationSpec,
    expand_observation_preset,
    observation_preset_aliases,
    observation_preset_families,
    observation_preset_hash,
    observation_preset_names,
    observation_preset_payload,
    observation_preset_registry,
)


def test_v3_observation_preset_registry_is_machine_readable():
    names = observation_preset_names()
    registry = observation_preset_registry()
    assert names == sorted(OBSERVATION_PRESETS.keys())
    assert set(registry.keys()) == set(OBSERVATION_PRESETS.keys())
    assert all(isinstance(v, list) and len(v) == 3 for v in registry.values())


def test_v3_observation_preset_alias_map_is_machine_readable():
    aliases = observation_preset_aliases()
    assert isinstance(aliases, dict)
    assert "rw_classical" in aliases


def test_v3_observation_preset_expansion_returns_legal_spec_with_traceable_metadata():
    spec = expand_observation_preset("classical_identity")
    assert isinstance(spec, ObservationSpec)
    assert spec.metadata["preset_name"] == "classical_identity"
    assert spec.metadata["preset_version"] == PRESET_VERSION


def test_v3_observation_preset_expansion_supports_aliases():
    direct = expand_observation_preset("classical_identity")
    alias = expand_observation_preset("rw_classical")
    assert alias.representation == direct.representation
    assert alias.context == direct.context
    assert alias.generalization == direct.generalization


def test_v3_observation_preset_unknown_name_fails_fast():
    with pytest.raises(ValueError, match="OBS_E_UNKNOWN_PRESET"):
        expand_observation_preset("not_a_real_preset")


def test_v3_observation_preset_payload_and_hash_are_deterministic():
    payload = observation_preset_payload("operant_vector")
    assert payload["preset_name"] == "operant_vector"
    assert payload["registry_version"] == PRESET_VERSION

    hashes = [observation_preset_hash("operant_vector") for _ in range(20)]
    assert len(set(hashes)) == 1


def test_v3_observation_preset_family_smoke_minimum_one_per_supported_family():
    families = observation_preset_families()
    assert families == OBSERVATION_PRESET_FAMILIES
    for presets in families.values():
        assert len(presets) >= 1
        for preset in presets:
            spec = expand_observation_preset(preset)
            assert isinstance(spec, ObservationSpec)

