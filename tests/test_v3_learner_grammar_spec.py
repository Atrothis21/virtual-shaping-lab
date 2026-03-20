from __future__ import annotations

import pytest

from virtual_shaping_lab.vsl.agent.learning import LearnerSpec


def _sample_spec() -> LearnerSpec:
    return LearnerSpec(
        trace="eligibility_trace",
        predictor="linear_value",
        error="td0",
        attention="mackintosh",
        updater="stochastic_gradient",
        policy="epsilon_greedy",
        metadata={"family": "td_control", "version": "3.5.0"},
    )


def test_v3_learner_spec_roundtrip():
    spec = _sample_spec()
    rebuilt = LearnerSpec.from_dict(spec.to_dict())
    assert rebuilt == spec


def test_v3_learner_spec_hash_is_stable():
    spec = _sample_spec()
    hashes = [spec.stable_hash() for _ in range(20)]
    assert len(set(hashes)) == 1


@pytest.mark.parametrize("field_name", ["trace", "predictor", "error", "attention", "updater", "policy"])
def test_v3_learner_spec_requires_non_empty_slot_values(field_name: str):
    payload = _sample_spec().to_dict()
    payload[field_name] = "   "
    with pytest.raises(ValueError, match=field_name):
        LearnerSpec.from_dict(payload)


def test_v3_learner_spec_requires_object_metadata():
    payload = _sample_spec().to_dict()
    payload["metadata"] = "bad"
    with pytest.raises(ValueError, match="metadata"):
        LearnerSpec.from_dict(payload)

