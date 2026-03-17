"""Core experiment runtime types for v2.1 orchestration."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any, Optional, TypedDict

import numpy as np

from virtual_shaping_lab.domain.types import Observation

SUPPORTED_TEMPLATE_SPEC_VERSIONS: tuple[int, ...] = (1,)


TrialSpec = dict[str, Any]


class TrialRecord(TypedDict, total=False):
    """
    Stable analysis/runtime record contract.

    Units may add extra keys, but these base keys should always be present
    after runtime finalization (with None/default values when not applicable).
    """

    phase: str | None
    phase_name: str | None
    protocol_name: str | None
    unit_path: str | None
    subphase: int | None
    subphase_name: str | None

    trial: int | None
    tick: int | None
    t_s: float | None
    dt_s: float | None
    trial_step: int | None
    trial_id: Any

    context: Any
    stimulus: Any
    stimulus_type: str | None
    action: Any
    response: Any
    reward: float | None
    prediction: float | None
    outcome_type: str | None
    schedule: str | None
    done: bool | None
    learning_enabled: bool | None

    metadata: dict[str, Any]


@dataclass(frozen=True)
class TrialTypeSpec:
    """Declarative trial-type definition for phase templates."""

    label: str
    stimuli: list[str]
    weight: float = 1.0

    def __post_init__(self) -> None:
        if not isinstance(self.label, str) or not self.label.strip():
            raise ValueError("TrialTypeSpec.label must be a non-empty string.")
        if not isinstance(self.stimuli, list) or not self.stimuli:
            raise ValueError("TrialTypeSpec.stimuli must be a non-empty list.")
        for stimulus in self.stimuli:
            if not isinstance(stimulus, str) or not stimulus.strip():
                raise ValueError("TrialTypeSpec.stimuli values must be non-empty strings.")
        if float(self.weight) <= 0.0:
            raise ValueError("TrialTypeSpec.weight must be > 0.")


@dataclass(frozen=True)
class LearningGateSpec:
    """Declarative learning toggle for a phase template."""

    enabled: bool = True
    mode: str = "always"
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class PavlovianContingencySpec:
    """Declarative Pavlovian contingency contract."""

    us_magnitude: float = 1.0
    us_event_type: str = "reward"
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.us_event_type, str) or not self.us_event_type.strip():
            raise ValueError("PavlovianContingencySpec.us_event_type must be a non-empty string.")


@dataclass(frozen=True)
class OperantContingencySpec:
    """Declarative operant contingency contract."""

    task_key: str = "operant"
    schedule_runtime: dict[str, Any] | None = None
    action_labels: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.task_key, str) or not self.task_key.strip():
            raise ValueError("OperantContingencySpec.task_key must be a non-empty string.")
        if self.schedule_runtime is not None and not isinstance(self.schedule_runtime, dict):
            raise ValueError("OperantContingencySpec.schedule_runtime must be an object when provided.")
        for action in self.action_labels:
            if not isinstance(action, str) or not action.strip():
                raise ValueError("OperantContingencySpec.action_labels values must be non-empty strings.")


ContingencySpec = PavlovianContingencySpec | OperantContingencySpec


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
class PhaseSpec:
    """
    Declarative phase-spec contract intended for plan-time serialization.

    This enables template-driven phases where behavior differences are
    represented by data, not class proliferation.
    """

    key: str
    name: str
    context_id: str | None
    n_trials: int
    time: TrialTimeSpec
    trial_types: list[TrialTypeSpec]
    contingency: ContingencySpec
    spec_version: int = 1
    learning: LearningGateSpec = field(default_factory=LearningGateSpec)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.key, str) or not self.key.strip():
            raise ValueError("PhaseSpec.key must be a non-empty string.")
        if not isinstance(self.name, str) or not self.name.strip():
            raise ValueError("PhaseSpec.name must be a non-empty string.")
        if self.context_id is not None and (not isinstance(self.context_id, str) or not self.context_id.strip()):
            raise ValueError("PhaseSpec.context_id must be a non-empty string when provided.")
        if int(self.n_trials) <= 0:
            raise ValueError("PhaseSpec.n_trials must be > 0.")
        if not isinstance(self.time, TrialTimeSpec):
            raise ValueError("PhaseSpec.time must be a TrialTimeSpec.")
        if not isinstance(self.trial_types, list) or not self.trial_types:
            raise ValueError("PhaseSpec.trial_types must be a non-empty list.")
        for tt in self.trial_types:
            if not isinstance(tt, TrialTypeSpec):
                raise ValueError("PhaseSpec.trial_types must contain TrialTypeSpec values.")
        if not isinstance(self.contingency, (PavlovianContingencySpec, OperantContingencySpec)):
            raise ValueError("PhaseSpec.contingency must be a supported contingency spec.")
        if int(self.spec_version) not in SUPPORTED_TEMPLATE_SPEC_VERSIONS:
            supported = ", ".join(str(v) for v in SUPPORTED_TEMPLATE_SPEC_VERSIONS)
            raise ValueError(
                f"Unsupported PhaseSpec.spec_version={self.spec_version}. Supported versions: {supported}."
            )
        if not isinstance(self.learning, LearningGateSpec):
            raise ValueError("PhaseSpec.learning must be a LearningGateSpec.")


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
    program_spec: dict[str, Any] = field(default_factory=dict)
    agent_spec: dict[str, Any] = field(default_factory=dict)
    runtime_spec: dict[str, Any] = field(default_factory=dict)
    analysis_spec: dict[str, Any] = field(default_factory=dict)
    canonical_payload: dict[str, Any] = field(default_factory=dict)
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
            "program_spec": self._to_primitive(self.program_spec),
            "agent_spec": self._to_primitive(self.agent_spec),
            "runtime_spec": self._to_primitive(self.runtime_spec),
            "analysis_spec": self._to_primitive(self.analysis_spec),
            "canonical_payload": self._to_primitive(self.canonical_payload),
            "seed": self.seed,
            "record_schema_version": self.record_schema_version,
            "settings": self._to_primitive(self.settings),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ExperimentPlan":
        """Rebuild an ExperimentPlan from to_dict-compatible data."""
        return cls(
            units=list(data.get("units", [])),
            program_spec=dict(data.get("program_spec", {}) or {}),
            agent_spec=dict(data.get("agent_spec", {}) or {}),
            runtime_spec=dict(data.get("runtime_spec", {}) or {}),
            analysis_spec=dict(data.get("analysis_spec", {}) or {}),
            canonical_payload=dict(data.get("canonical_payload", {}) or {}),
            seed=data.get("seed"),
            record_schema_version=data.get("record_schema_version", "v1"),
            settings=dict(data.get("settings", {}) or {}),
        )

    def stable_hash(self) -> str:
        """Stable content hash for caching/replay identity."""
        identity = {
            "canonical_payload": self._to_primitive(self.canonical_payload),
            "record_schema_version": self.record_schema_version,
        }
        payload = json.dumps(identity, sort_keys=True, separators=(",", ":"))
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
