from __future__ import annotations

import pytest

from virtual_shaping_lab.vsl.agent.observation import ObservationOutput, normalize_observation_output_dict


def _canonical_payload() -> dict:
    return {
        "raw_stimulus": {"cue": "tone"},
        "representation": {"x": [1.0, 0.0]},
        "context_state": {"ctx": "A"},
        "generalized_state": {"g": [1.0, 0.4]},
        "features": [1.0, 0.4],
        "feature_names": ["tone", "similarity"],
        "metadata": {"source": "slice2"},
    }


def test_v3_observation_output_roundtrip():
    payload = _canonical_payload()
    out = ObservationOutput.from_dict(payload)
    assert out.to_dict() == payload


def test_v3_observation_output_accepts_legacy_alias_names():
    legacy = {
        "raw_observation": {"cue": "tone"},
        "state_representation": {"x": [1.0, 0.0]},
        "context": {"ctx": "A"},
        "generalized": {"g": [1.0, 0.4]},
        "feature_vector": [1.0, 0.4],
        "feature_labels": ["tone", "similarity"],
        "metadata": {"source": "legacy"},
    }
    normalized = normalize_observation_output_dict(legacy)
    assert set(normalized.keys()) == {
        "raw_stimulus",
        "representation",
        "context_state",
        "generalized_state",
        "features",
        "feature_names",
        "metadata",
    }
    out = ObservationOutput.from_dict(legacy)
    assert out.feature_names == ["tone", "similarity"]
    assert out.features == [1.0, 0.4]


def test_v3_observation_output_rejects_non_numeric_features():
    payload = _canonical_payload()
    payload["features"] = ["bad"]
    with pytest.raises(ValueError, match="features must contain numeric"):
        ObservationOutput.from_dict(payload)


def test_v3_observation_output_rejects_feature_name_count_mismatch():
    payload = _canonical_payload()
    payload["feature_names"] = ["tone"]
    with pytest.raises(ValueError, match="feature_names must be empty or match"):
        ObservationOutput.from_dict(payload)

