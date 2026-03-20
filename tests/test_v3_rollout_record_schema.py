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
        metadata={"source": "env"},
    )
    record = step_to_rollout_record(step)
    assert record.schema_version == "v1"
    assert record.step_index == 3
    assert record.segment_key == "seg0"
