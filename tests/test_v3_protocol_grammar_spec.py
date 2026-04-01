from __future__ import annotations

import pytest

from virtual_shaping_lab.vsl.protocol import ProtocolSpec, ProtocolSpecValidationError


def _sample_spec() -> ProtocolSpec:
    return ProtocolSpec(
        emission_rule="operant_offer_emission",
        consequence_rule="scheduled_consequence",
        advance_rule="trial_increment",
        stop_rule="n_trials",
        protocol_family="operant_conditioning",
        action_space_mode="discrete",
        temporal_mode="trial_discrete",
        schedule_metadata={"reward_schedule": "vr10"},
        phase_metadata={"phase_name": "Operant"},
        metadata={"family": "operant", "version": "3.21.0"},
    )


def test_v3_protocol_spec_roundtrip():
    spec = _sample_spec()
    rebuilt = ProtocolSpec.from_dict(spec.to_dict())
    assert rebuilt == spec


def test_v3_protocol_spec_hash_is_stable():
    spec = _sample_spec()
    hashes = [spec.stable_hash() for _ in range(20)]
    assert len(set(hashes)) == 1


@pytest.mark.parametrize(
    "field_name",
    [
        "emission_rule",
        "consequence_rule",
        "advance_rule",
        "stop_rule",
        "protocol_family",
        "action_space_mode",
        "temporal_mode",
    ],
)
def test_v3_protocol_spec_requires_non_empty_slot_values(field_name: str):
    payload = _sample_spec().to_dict()
    payload[field_name] = "   "
    with pytest.raises(ValueError, match=field_name):
        ProtocolSpec.from_dict(payload)


@pytest.mark.parametrize("field_name", ["schedule_metadata", "phase_metadata", "metadata"])
def test_v3_protocol_spec_requires_object_maps(field_name: str):
    payload = _sample_spec().to_dict()
    payload[field_name] = "bad"
    with pytest.raises(ValueError, match=field_name):
        ProtocolSpec.from_dict(payload)


def test_v3_protocol_spec_fails_fast_for_illegal_tuple():
    with pytest.raises(ProtocolSpecValidationError, match="PROTO_E_OPERANT_REQUIRES_ACTION_SPACE"):
        ProtocolSpec(
            emission_rule="operant_offer_emission",
            consequence_rule="deterministic_consequence",
            advance_rule="trial_increment",
            stop_rule="n_trials",
            protocol_family="operant_conditioning",
            action_space_mode="classical_none",
            temporal_mode="trial_discrete",
        )
