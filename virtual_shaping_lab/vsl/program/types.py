"""Typed environment-program structures for V3 compilation slices."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any


def _to_primitive(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(k): _to_primitive(v) for k, v in sorted(value.items(), key=lambda item: str(item[0]))}
    if isinstance(value, list):
        return [_to_primitive(v) for v in value]
    if isinstance(value, tuple):
        return [_to_primitive(v) for v in value]
    if hasattr(value, "to_dict"):
        return _to_primitive(value.to_dict())
    return value


@dataclass(frozen=True)
class EventSpec:
    """Declarative event descriptor inside a trial."""

    event_type: str
    start_s: float
    end_s: float
    magnitude: float = 1.0
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.event_type, str) or not self.event_type.strip():
            raise ValueError("EventSpec.event_type must be a non-empty string.")
        if self.start_s < 0.0:
            raise ValueError("EventSpec.start_s must be >= 0.")
        if self.end_s <= self.start_s:
            raise ValueError("EventSpec.end_s must be > start_s.")
        if not isinstance(self.metadata, dict):
            raise ValueError("EventSpec.metadata must be an object.")

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_type": self.event_type,
            "start_s": float(self.start_s),
            "end_s": float(self.end_s),
            "magnitude": float(self.magnitude),
            "metadata": _to_primitive(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "EventSpec":
        return cls(
            event_type=str(data.get("event_type", "")).strip(),
            start_s=float(data.get("start_s", 0.0)),
            end_s=float(data.get("end_s", 0.0)),
            magnitude=float(data.get("magnitude", 1.0)),
            metadata=dict(data.get("metadata", {}) or {}),
        )


@dataclass(frozen=True)
class TrialSpec:
    """Declarative trial-level environment program step."""

    trial_type: str
    n_trials: int = 1
    stimuli: dict[str, Any] = field(default_factory=dict)
    params: dict[str, Any] = field(default_factory=dict)
    events: list[EventSpec] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.trial_type, str) or not self.trial_type.strip():
            raise ValueError("TrialSpec.trial_type must be a non-empty string.")
        if int(self.n_trials) <= 0:
            raise ValueError("TrialSpec.n_trials must be > 0.")
        if not isinstance(self.stimuli, dict):
            raise ValueError("TrialSpec.stimuli must be an object.")
        if not isinstance(self.params, dict):
            raise ValueError("TrialSpec.params must be an object.")
        if not isinstance(self.events, list):
            raise ValueError("TrialSpec.events must be a list.")
        for event in self.events:
            if not isinstance(event, EventSpec):
                raise ValueError("TrialSpec.events must contain EventSpec values.")
        if not isinstance(self.metadata, dict):
            raise ValueError("TrialSpec.metadata must be an object.")

    def to_dict(self) -> dict[str, Any]:
        return {
            "trial_type": self.trial_type,
            "n_trials": int(self.n_trials),
            "stimuli": _to_primitive(self.stimuli),
            "params": _to_primitive(self.params),
            "events": [_to_primitive(e) for e in self.events],
            "metadata": _to_primitive(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "TrialSpec":
        raw_events = list(data.get("events", []) or [])
        return cls(
            trial_type=str(data.get("trial_type", "")).strip(),
            n_trials=int(data.get("n_trials", 1)),
            stimuli=dict(data.get("stimuli", {}) or {}),
            params=dict(data.get("params", {}) or {}),
            events=[EventSpec.from_dict(e) if isinstance(e, dict) else e for e in raw_events],
            metadata=dict(data.get("metadata", {}) or {}),
        )


@dataclass(frozen=True)
class EnvironmentSegment:
    """A compiled environment segment (phase/protocol-derived)."""

    key: str
    name: str
    protocol: str
    trials: list[TrialSpec] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.key, str) or not self.key.strip():
            raise ValueError("EnvironmentSegment.key must be a non-empty string.")
        if not isinstance(self.name, str) or not self.name.strip():
            raise ValueError("EnvironmentSegment.name must be a non-empty string.")
        if not isinstance(self.protocol, str) or not self.protocol.strip():
            raise ValueError("EnvironmentSegment.protocol must be a non-empty string.")
        if not isinstance(self.trials, list):
            raise ValueError("EnvironmentSegment.trials must be a list.")
        if not self.trials:
            raise ValueError("EnvironmentSegment.trials must be non-empty.")
        for trial in self.trials:
            if not isinstance(trial, TrialSpec):
                raise ValueError("EnvironmentSegment.trials must contain TrialSpec values.")
        if not isinstance(self.metadata, dict):
            raise ValueError("EnvironmentSegment.metadata must be an object.")

    def to_dict(self) -> dict[str, Any]:
        return {
            "key": self.key,
            "name": self.name,
            "protocol": self.protocol,
            "trials": [_to_primitive(t) for t in self.trials],
            "metadata": _to_primitive(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "EnvironmentSegment":
        raw_trials = list(data.get("trials", []) or [])
        return cls(
            key=str(data.get("key", "")).strip(),
            name=str(data.get("name", "")).strip(),
            protocol=str(data.get("protocol", "")).strip(),
            trials=[TrialSpec.from_dict(t) if isinstance(t, dict) else t for t in raw_trials],
            metadata=dict(data.get("metadata", {}) or {}),
        )


@dataclass(frozen=True)
class EnvironmentProgram:
    """Compiled environment program made of ordered segments."""

    segments: list[EnvironmentSegment] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.segments, list):
            raise ValueError("EnvironmentProgram.segments must be a list.")
        if not self.segments:
            raise ValueError("EnvironmentProgram.segments must be non-empty.")
        for segment in self.segments:
            if not isinstance(segment, EnvironmentSegment):
                raise ValueError("EnvironmentProgram.segments must contain EnvironmentSegment values.")
        if not isinstance(self.metadata, dict):
            raise ValueError("EnvironmentProgram.metadata must be an object.")

    def to_dict(self) -> dict[str, Any]:
        return {
            "segments": [_to_primitive(s) for s in self.segments],
            "metadata": _to_primitive(self.metadata),
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), sort_keys=True, separators=(",", ":"))

    def stable_hash(self) -> str:
        return hashlib.sha256(self.to_json().encode("utf-8")).hexdigest()

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "EnvironmentProgram":
        raw_segments = list(data.get("segments", []) or [])
        return cls(
            segments=[EnvironmentSegment.from_dict(s) if isinstance(s, dict) else s for s in raw_segments],
            metadata=dict(data.get("metadata", {}) or {}),
        )
