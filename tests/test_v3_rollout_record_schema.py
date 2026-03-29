from __future__ import annotations

import pytest

from virtual_shaping_lab.vsl.records import (
    ROLLOUT_RECORD_SCHEMA_VERSION,
    SUPPORTED_ROLLOUT_RECORD_SCHEMA_VERSIONS,
    RolloutRecord,
    normalize_rollout_record,
    validate_rollout_record_migration,
)
from virtual_shaping_lab.vsl.rollout import step_to_rollout_record
from virtual_shaping_lab.vsl.environment import EnvironmentStep, EnvironmentTermination


def _sample() -> RolloutRecord:
    return RolloutRecord(
        schema_version=ROLLOUT_RECORD_SCHEMA_VERSION,
        rollout_id="rollout_0",
        episode_id=0,
        segment_index=0,
        step_index=0,
        segment_key="acquisition_0",
        protocol="acquisition",
        trial_type="cs_plus",
        trial_index=0,
        action=None,
        stimulus={"cs_plus": ["tone"]},
        reward=1.0,
        done=False,
        trial_state={"s": {}, "x": {}, "z": {}, "w": {}, "a": {}, "u": {}, "y": 1.0, "m": {}},
        termination={"done": False, "reason": "running", "metadata": {}},
        metadata={"source": "test"},
    )


def test_v3_rollout_record_schema_version_is_locked():
    assert ROLLOUT_RECORD_SCHEMA_VERSION == "v1"
    assert SUPPORTED_ROLLOUT_RECORD_SCHEMA_VERSIONS == ("v1",)


def test_v3_rollout_record_roundtrip_and_hash_stability():
    record = _sample()
    rebuilt = RolloutRecord.from_dict(record.to_dict())
    assert rebuilt.to_dict() == record.to_dict()
    hashes = [record.stable_hash() for _ in range(10)]
    assert len(set(hashes)) == 1


def test_v3_rollout_record_requires_core_fields():
    with pytest.raises(ValueError, match="segment_key"):
        RolloutRecord(segment_key="", protocol="acquisition", trial_type="cs_plus")
    with pytest.raises(ValueError, match="protocol"):
        RolloutRecord(segment_key="seg0", protocol="", trial_type="cs_plus")
    with pytest.raises(ValueError, match="trial_type"):
        RolloutRecord(segment_key="seg0", protocol="acquisition", trial_type="")
    with pytest.raises(ValueError, match="rollout_id"):
        RolloutRecord(rollout_id=" ", segment_key="seg0", protocol="acquisition", trial_type="cs_plus")
    with pytest.raises(ValueError, match="episode_id"):
        RolloutRecord(episode_id=-1, segment_key="seg0", protocol="acquisition", trial_type="cs_plus")
    with pytest.raises(ValueError, match="segment_index"):
        RolloutRecord(segment_index=-1, segment_key="seg0", protocol="acquisition", trial_type="cs_plus")


def test_v3_rollout_record_schema_migration_policy_rejects_unsupported():
    validate_rollout_record_migration(from_version="v1", to_version="v1")
    with pytest.raises(ValueError, match="Unsupported rollout record schema migration"):
        validate_rollout_record_migration(from_version="v1", to_version="v2")


def test_v3_rollout_record_normalization_is_schema_aware():
    payload = {
        "step_index": 1,
        "segment_key": "seg",
        "protocol": "acquisition",
        "trial_type": "cs_plus",
        "trial_index": 0,
        "stimulus": {},
        "done": False,
        "termination": {},
        "metadata": {},
    }
    normalized = normalize_rollout_record(payload, from_version="v1", to_version="v1")
    assert normalized["schema_version"] == "v1"
    with pytest.raises(ValueError, match="Unsupported rollout record schema migration"):
        normalize_rollout_record(payload, from_version="v1", to_version="v2")


def test_v3_rollout_step_adapter_emits_locked_schema_record():
    step = EnvironmentStep(
        step_index=3,
        segment_key="seg0",
        protocol="acquisition",
        trial_type="cs_plus",
        trial_index=1,
        action=None,
        stimulus={"cs_plus": ["tone"]},
        reward=1.0,
        done=False,
        termination=EnvironmentTermination(done=False, reason="running"),
        metadata={"source": "env", "segment_index": 7},
    )
    record = step_to_rollout_record(step, rollout_id="rollout_5", episode_id=2)
    assert record.schema_version == "v1"
    assert record.step_index == 3
    assert record.segment_key == "seg0"
    assert record.rollout_id == "rollout_5"
    assert record.episode_id == 2
    assert record.segment_index == 7


def test_v3_rollout_step_adapter_promotes_learner_traces_into_record_metadata():
    step = EnvironmentStep(
        step_index=4,
        segment_key="seg1",
        protocol="acquisition",
        trial_type="cs_plus",
        trial_index=2,
        action=None,
        stimulus={"cs_plus": ["tone"]},
        reward=1.0,
        done=False,
        termination=EnvironmentTermination(done=False, reason="running"),
        metadata={
            "learner": {
                "prediction": 0.25,
                "error": 0.75,
                "update_features": {"tone": 1.0},
                "attention_state": {"tone": 0.6},
                "eligibility_state": {"tone": 0.4},
            }
        },
    )
    record = step_to_rollout_record(step)
    assert record.metadata["learner_traces"] == {
        "v": 0.25,
        "delta": 0.75,
        "theta": {"tone": 1.0},
        "attention": {"tone": 0.6},
        "memory": {"tone": 0.4},
    }


def test_v3_rollout_step_adapter_promotes_observation_traces_into_record_metadata():
    step = EnvironmentStep(
        step_index=5,
        segment_key="seg2",
        protocol="acquisition",
        trial_type="cs_plus",
        trial_index=3,
        action=None,
        stimulus={"cs_plus": ["tone"]},
        reward=1.0,
        done=False,
        termination=EnvironmentTermination(done=False, reason="running"),
        metadata={
            "observation": {
                "output": {
                    "representation": {"tone": 1.0},
                    "context_state": "A",
                    "generalized_state": {"kind": "identity"},
                    "features": [1.0, 0.0],
                    "feature_names": ["tone", "ctx:A"],
                    "metadata": {
                        "runtime_observation": {"preset_name": "identity_observation"},
                        "stage_traces": {"representation": {"feature_names": ["tone"]}},
                    },
                },
            }
        },
    )
    record = step_to_rollout_record(step)
    assert record.metadata["observation_traces"] == {
        "representation": {"tone": 1.0},
        "context_state": "A",
        "generalized_state": {"kind": "identity"},
        "features": [1.0, 0.0],
        "feature_names": ["tone", "ctx:A"],
        "provenance": {
            "runtime_observation": {"preset_name": "identity_observation"},
            "stage_traces": {"representation": {"feature_names": ["tone"]}},
        },
    }
