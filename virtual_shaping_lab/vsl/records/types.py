"""V3 rollout-record schema and versioning rules."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any

ROLLOUT_RECORD_SCHEMA_VERSION = "v1"
SUPPORTED_ROLLOUT_RECORD_SCHEMA_VERSIONS: tuple[str, ...] = (ROLLOUT_RECORD_SCHEMA_VERSION,)


def _to_primitive(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(k): _to_primitive(v) for k, v in sorted(value.items(), key=lambda item: str(item[0]))}
    if isinstance(value, list):
        return [_to_primitive(v) for v in value]
    if isinstance(value, tuple):
        return [_to_primitive(v) for v in value]
    return value


def _coerce_schema_version(value: Any) -> str:
    version = str(value or ROLLOUT_RECORD_SCHEMA_VERSION).strip()
    if version not in SUPPORTED_ROLLOUT_RECORD_SCHEMA_VERSIONS:
        supported = ", ".join(SUPPORTED_ROLLOUT_RECORD_SCHEMA_VERSIONS)
        raise ValueError(f"Unsupported rollout record schema version '{version}'. Supported versions: {supported}")
    return version


def validate_rollout_record_migration(*, from_version: str, to_version: str) -> None:
    source_raw = str(from_version or ROLLOUT_RECORD_SCHEMA_VERSION).strip()
    target_raw = str(to_version or ROLLOUT_RECORD_SCHEMA_VERSION).strip()
    if source_raw not in SUPPORTED_ROLLOUT_RECORD_SCHEMA_VERSIONS:
        raise ValueError(
            f"Unsupported rollout record schema migration: {source_raw} -> {target_raw}"
        )
    if target_raw not in SUPPORTED_ROLLOUT_RECORD_SCHEMA_VERSIONS:
        raise ValueError(
            f"Unsupported rollout record schema migration: {source_raw} -> {target_raw}"
        )
    source = _coerce_schema_version(source_raw)
    target = _coerce_schema_version(target_raw)
    if source != target:
        raise ValueError(f"Unsupported rollout record schema migration: {source} -> {target}")


@dataclass(frozen=True)
class RolloutRecord:
    """Stable V3 record boundary for environment rollouts."""

    schema_version: str = ROLLOUT_RECORD_SCHEMA_VERSION
    step_index: int = 0
    segment_key: str = ""
    protocol: str = ""
    trial_type: str = ""
    trial_index: int = 0
    action: Any = None
    stimulus: dict[str, Any] = field(default_factory=dict)
    reward: float = 0.0
    done: bool = False
    trial_state: dict[str, Any] | None = None
    termination: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "schema_version", _coerce_schema_version(self.schema_version))
        if int(self.step_index) < 0:
            raise ValueError("RolloutRecord.step_index must be >= 0.")
        if int(self.trial_index) < 0:
            raise ValueError("RolloutRecord.trial_index must be >= 0.")
        if not isinstance(self.segment_key, str) or not self.segment_key.strip():
            raise ValueError("RolloutRecord.segment_key must be a non-empty string.")
        if not isinstance(self.protocol, str) or not self.protocol.strip():
            raise ValueError("RolloutRecord.protocol must be a non-empty string.")
        if not isinstance(self.trial_type, str) or not self.trial_type.strip():
            raise ValueError("RolloutRecord.trial_type must be a non-empty string.")
        if not isinstance(self.stimulus, dict):
            raise ValueError("RolloutRecord.stimulus must be an object.")
        if not isinstance(self.done, bool):
            raise ValueError("RolloutRecord.done must be a bool.")
        if self.trial_state is not None and not isinstance(self.trial_state, dict):
            raise ValueError("RolloutRecord.trial_state must be an object when provided.")
        if not isinstance(self.termination, dict):
            raise ValueError("RolloutRecord.termination must be an object.")
        if not isinstance(self.metadata, dict):
            raise ValueError("RolloutRecord.metadata must be an object.")

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "step_index": int(self.step_index),
            "segment_key": self.segment_key,
            "protocol": self.protocol,
            "trial_type": self.trial_type,
            "trial_index": int(self.trial_index),
            "action": self.action,
            "stimulus": _to_primitive(self.stimulus),
            "reward": float(self.reward),
            "done": bool(self.done),
            "trial_state": _to_primitive(self.trial_state) if self.trial_state is not None else None,
            "termination": _to_primitive(self.termination),
            "metadata": _to_primitive(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "RolloutRecord":
        return cls(
            schema_version=data.get("schema_version", ROLLOUT_RECORD_SCHEMA_VERSION),
            step_index=int(data.get("step_index", 0)),
            segment_key=str(data.get("segment_key", "")),
            protocol=str(data.get("protocol", "")),
            trial_type=str(data.get("trial_type", "")),
            trial_index=int(data.get("trial_index", 0)),
            action=data.get("action"),
            stimulus=dict(data.get("stimulus", {}) or {}),
            reward=float(data.get("reward", 0.0)),
            done=bool(data.get("done", False)),
            trial_state=dict(data.get("trial_state", {})) if isinstance(data.get("trial_state"), dict) else None,
            termination=dict(data.get("termination", {}) or {}),
            metadata=dict(data.get("metadata", {}) or {}),
        )

    def stable_hash(self) -> str:
        blob = json.dumps(self.to_dict(), sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def normalize_rollout_record(
    record: dict[str, Any],
    *,
    from_version: str = ROLLOUT_RECORD_SCHEMA_VERSION,
    to_version: str = ROLLOUT_RECORD_SCHEMA_VERSION,
) -> dict[str, Any]:
    validate_rollout_record_migration(from_version=from_version, to_version=to_version)
    normalized = dict(record or {})
    normalized.setdefault("schema_version", to_version)
    return RolloutRecord.from_dict(normalized).to_dict()
