from __future__ import annotations

import pytest

from virtual_shaping_lab.vsl.agent.policy import PolicySpec, PolicySpecValidationError


def _sample_spec() -> PolicySpec:
    return PolicySpec(
        selection_rule="epsilon_greedy",
        action_space_mode="discrete",
        parameters={"epsilon": 0.2},
        tie_break_rule="random",
        availability_rule="environment_declared",
        metadata={"family": "operant", "version": "3.20.0"},
    )


def test_v3_policy_spec_roundtrip():
    spec = _sample_spec()
    rebuilt = PolicySpec.from_dict(spec.to_dict())
    assert rebuilt == spec


def test_v3_policy_spec_hash_is_stable():
    spec = _sample_spec()
    hashes = [spec.stable_hash() for _ in range(20)]
    assert len(set(hashes)) == 1


@pytest.mark.parametrize("field_name", ["selection_rule", "action_space_mode"])
def test_v3_policy_spec_requires_non_empty_slot_values(field_name: str):
    payload = _sample_spec().to_dict()
    payload[field_name] = "   "
    with pytest.raises(ValueError, match=field_name):
        PolicySpec.from_dict(payload)


@pytest.mark.parametrize("field_name", ["parameters", "metadata"])
def test_v3_policy_spec_requires_object_maps(field_name: str):
    payload = _sample_spec().to_dict()
    payload[field_name] = "bad"
    with pytest.raises(ValueError, match=field_name):
        PolicySpec.from_dict(payload)


def test_v3_policy_spec_fails_fast_for_illegal_tuple():
    with pytest.raises(PolicySpecValidationError, match="POL_E_NULL_REQUIRES_CLASSICAL_NONE"):
        PolicySpec(
            selection_rule="null",
            action_space_mode="discrete",
            parameters={},
        )

