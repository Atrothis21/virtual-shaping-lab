from __future__ import annotations

from virtual_shaping_lab.vsl.agent.policy import (
    POLICY_REGISTRY_VERSION,
    compatibility_matrix,
    policy_registry_hash,
    policy_registry_payload,
    slot_registries,
)


def test_v3_policy_registry_slots_and_compatibility_are_present():
    slots = slot_registries()
    matrix = compatibility_matrix()
    assert set(slots.keys()) == {"selection_rule", "action_space_mode", "tie_break_rule", "availability_rule"}
    assert "selection_to_action_space" in matrix
    assert "selection_required_parameters" in matrix


def test_v3_policy_registry_payload_is_versioned():
    payload = policy_registry_payload()
    assert payload["version"] == POLICY_REGISTRY_VERSION
    assert "slot_registries" in payload
    assert "compatibility_matrix" in payload


def test_v3_policy_registry_hash_is_stable():
    hashes = [policy_registry_hash() for _ in range(20)]
    assert len(set(hashes)) == 1

