from __future__ import annotations

import pytest

from virtual_shaping_lab.vsl.agent.policy import (
    POLICY_PRESETS,
    expand_policy_preset,
    policy_preset_aliases,
    policy_preset_families,
    policy_preset_hash,
    policy_preset_names,
    policy_preset_payload,
    policy_preset_registry,
)


def test_v3_policy_preset_registry_is_deterministic():
    names = policy_preset_names()
    registry = policy_preset_registry()
    assert names == sorted(POLICY_PRESETS.keys())
    assert set(registry.keys()) == set(names)


def test_v3_policy_preset_aliases_and_families_have_entries():
    aliases = policy_preset_aliases()
    families = policy_preset_families()
    assert "no_policy" in aliases
    assert "operant" in families


def test_v3_policy_preset_payload_and_hash_are_stable():
    payload = policy_preset_payload("epsilon_greedy")
    assert payload["preset_name"] == "operant_epsilon_greedy"
    hashes = [policy_preset_hash("epsilon_greedy") for _ in range(20)]
    assert len(set(hashes)) == 1


def test_v3_policy_preset_expand_unknown_raises():
    with pytest.raises(ValueError, match="POL_E_UNKNOWN_PRESET"):
        expand_policy_preset("unknown_preset")

