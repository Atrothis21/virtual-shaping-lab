from __future__ import annotations

import pytest

from virtual_shaping_lab.vsl.protocol import (
    PROTOCOL_PRESETS,
    expand_protocol_preset,
    protocol_preset_aliases,
    protocol_preset_families,
    protocol_preset_hash,
    protocol_preset_names,
    protocol_preset_payload,
    protocol_preset_registry,
)


def test_v3_protocol_preset_registry_is_deterministic():
    names = protocol_preset_names()
    registry = protocol_preset_registry()
    assert names == sorted(PROTOCOL_PRESETS.keys())
    assert set(registry.keys()) == set(names)


def test_v3_protocol_preset_aliases_and_families_have_entries():
    aliases = protocol_preset_aliases()
    families = protocol_preset_families()
    assert "operant" in aliases
    assert "classical" in families


def test_v3_protocol_preset_payload_and_hash_are_stable():
    payload = protocol_preset_payload("operant")
    assert payload["preset_name"] == "operant_trial_discrete"
    hashes = [protocol_preset_hash("operant") for _ in range(20)]
    assert len(set(hashes)) == 1


def test_v3_protocol_preset_expand_unknown_raises():
    with pytest.raises(ValueError, match="PROTO_E_UNKNOWN_PRESET"):
        expand_protocol_preset("unknown_preset")
