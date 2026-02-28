"""Core experiment runtime types for v2.1 orchestration."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any, Optional

import numpy as np

from virtual_shaping_lab.domain.types import Observation


TrialSpec = dict[str, Any]
TrialRecord = dict[str, Any]


def _is_time_grid_aligned(duration_s: float, dt_s: float, tol: float = 1e-9) -> bool:
    steps = duration_s / dt_s
    return abs(steps - round(steps)) <= tol


@dataclass(frozen=True)
class EventSpec:
    """Intra-trial event window (e.g., CS/US/context on-off span)."""

    event_type: str
    start_s: float
    end_s: float
    magnitude: float = 1.0
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.start_s < 0.0:
            raise ValueError("EventSpec.start_s must be >= 0.")
        if self.end_s <= self.start_s:
            raise ValueError("EventSpec.end_s must be > start_s.")


@dataclass(frozen=True)
class WindowSpec:
    """Optional response/availability window inside a trial."""

    start_s: float
    end_s: float
    label: str = "window"
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.start_s < 0.0:
            raise ValueError("WindowSpec.start_s must be >= 0.")
        if self.end_s <= self.start_s:
            raise ValueError("WindowSpec.end_s must be > start_s.")


@dataclass(frozen=True)
class TrialTimeSpec:
    """
    Validated time-grid contract for a single trial.

    Keeps timing logic out of runner/phase wiring while making constraints explicit.
    """

    duration_s: float
    dt_s: float
    iti_s: float = 0.0
    allow_partial_last_step: bool = False
    events: list[EventSpec] = field(default_factory=list)
    response_windows: list[WindowSpec] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.duration_s <= 0.0:
            raise ValueError("TrialTimeSpec.duration_s must be > 0.")
        if self.dt_s <= 0.0:
            raise ValueError("TrialTimeSpec.dt_s must be > 0.")
        if self.iti_s < 0.0:
            raise ValueError("TrialTimeSpec.iti_s must be >= 0.")
        if not self.allow_partial_last_step and not _is_time_grid_aligned(self.duration_s, self.dt_s):
            raise ValueError(
                "TrialTimeSpec duration_s must align to dt_s when allow_partial_last_step is False."
            )
        for e in self.events:
            if e.end_s > self.duration_s + 1e-9:
                raise ValueError("EventSpec end_s must be within trial duration_s.")
        for w in self.response_windows:
            if w.end_s > self.duration_s + 1e-9:
                raise ValueError("WindowSpec end_s must be within trial duration_s.")


@dataclass(frozen=True)
class TrialSchedule:
    """
    Executable trial schedule used by tick-based runtime paths.

    A phase can provide this in StepResult metadata so runtime can execute
    intra-trial ticks without embedding phase logic in the runner.
    """

    time: TrialTimeSpec
    base_stimuli: list[Any] = field(default_factory=list)
    available_actions: list[Any] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class StepResult:
    """
    Single execution step produced by a runnable unit.

    This is intentionally generic so phases/protocol adapters can adopt it
    incrementally without forcing a tick-based rewrite.
    """

    observation: Observation
    available_actions: list[Any] = field(default_factory=list)
    reward: float = 0.0
    learning_enabled: bool = True
    done: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ExperimentPlan:
    """
    Declarative runtime plan.

    `units` may contain pre-built unit configs or runtime identifiers depending
    on assembly stage.
    """

    units: list[Any]
    seed: Optional[int] = None
    record_schema_version: str = "v1"
    settings: dict[str, Any] = field(default_factory=dict)

    @staticmethod
    def _to_primitive(value: Any) -> Any:
        if isinstance(value, dict):
            return {str(k): ExperimentPlan._to_primitive(v) for k, v in sorted(value.items(), key=lambda item: str(item[0]))}
        if isinstance(value, list):
            return [ExperimentPlan._to_primitive(v) for v in value]
        if isinstance(value, tuple):
            return [ExperimentPlan._to_primitive(v) for v in value]
        return value

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable deterministic dict representation."""
        return {
            "units": self._to_primitive(self.units),
            "seed": self.seed,
            "record_schema_version": self.record_schema_version,
            "settings": self._to_primitive(self.settings),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ExperimentPlan":
        """Rebuild an ExperimentPlan from to_dict-compatible data."""
        return cls(
            units=list(data.get("units", [])),
            seed=data.get("seed"),
            record_schema_version=data.get("record_schema_version", "v1"),
            settings=dict(data.get("settings", {}) or {}),
        )

    def stable_hash(self) -> str:
        """Stable content hash for caching/replay identity."""
        payload = json.dumps(self.to_dict(), sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()


@dataclass
class ExperimentContext:
    """Shared mutable runtime context passed across runner and units."""

    agent: Any
    rng: np.random.Generator
    clock_s: float = 0.0
    shared_state: dict[str, Any] = field(default_factory=dict)
    settings: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class RunResult:
    """Execution result envelope for top-level experiment runs."""

    run_id: str
    records: list[TrialRecord] = field(default_factory=list)
    artifacts: dict[str, Any] = field(default_factory=dict)
