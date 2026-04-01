from __future__ import annotations

from virtual_shaping_lab.vsl.protocol import (
    PROTOCOL_REGISTRY_VERSION,
    compatibility_matrix,
    protocol_registry_hash,
    protocol_registry_payload,
    slot_registries,
)


def test_v3_protocol_registry_slots_and_compatibility_are_present():
    slots = slot_registries()
    matrix = compatibility_matrix()
    assert set(slots.keys()) == {
        "emission_rule",
        "consequence_rule",
        "advance_rule",
        "stop_rule",
        "protocol_family",
        "action_space_mode",
        "temporal_mode",
    }
    assert "family_to_action_space" in matrix
    assert "temporal_to_advance" in matrix


def test_v3_protocol_registry_payload_is_versioned():
    payload = protocol_registry_payload()
    assert payload["version"] == PROTOCOL_REGISTRY_VERSION
    assert "slot_registries" in payload
    assert "compatibility_matrix" in payload


def test_v3_protocol_registry_hash_is_stable():
    hashes = [protocol_registry_hash() for _ in range(20)]
    assert len(set(hashes)) == 1
