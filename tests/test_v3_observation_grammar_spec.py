from __future__ import annotations

import pytest

from virtual_shaping_lab.vsl.agent.observation import ObservationSpec, ObservationSpecValidationError


def _sample_spec() -> ObservationSpec:
    return ObservationSpec(
        representation="temporal_basis",
        context="discrete_context",
        generalization="context_gate",
        metadata={"family": "operant", "version": "3.19.0"},
    )


def test_v3_observation_spec_roundtrip():
    spec = _sample_spec()
    rebuilt = ObservationSpec.from_dict(spec.to_dict())
    assert rebuilt == spec


def test_v3_observation_spec_hash_is_stable():
    spec = _sample_spec()
    hashes = [spec.stable_hash() for _ in range(20)]
    assert len(set(hashes)) == 1


@pytest.mark.parametrize("field_name", ["representation", "context", "generalization"])
def test_v3_observation_spec_requires_non_empty_slot_values(field_name: str):
    payload = _sample_spec().to_dict()
    payload[field_name] = "   "
    with pytest.raises(ValueError, match=field_name):
        ObservationSpec.from_dict(payload)


def test_v3_observation_spec_requires_object_metadata():
    payload = _sample_spec().to_dict()
    payload["metadata"] = "bad"
    with pytest.raises(ValueError, match="metadata"):
        ObservationSpec.from_dict(payload)


def test_v3_observation_spec_fails_fast_for_illegal_tuple():
    with pytest.raises(ObservationSpecValidationError, match="OBS_E_GENERALIZATION_REQUIRES_CONTEXT"):
        ObservationSpec(
            representation="temporal_basis",
            context="none",
            generalization="context_gate",
        )

