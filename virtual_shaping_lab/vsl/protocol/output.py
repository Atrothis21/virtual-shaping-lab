"""Typed protocol stage outputs for executable protocol operators."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class EmissionOutput:
    """Output of protocol-side emission stage."""

    stimulus: dict[str, float] = field(default_factory=dict)
    context: str | None = None
    available_actions: tuple[Any, ...] = field(default_factory=tuple)
    emission_state: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.stimulus, dict):
            raise ValueError("EmissionOutput.stimulus must be an object.")
        if not isinstance(self.emission_state, dict):
            raise ValueError("EmissionOutput.emission_state must be an object.")
        if not isinstance(self.metadata, dict):
            raise ValueError("EmissionOutput.metadata must be an object.")
        object.__setattr__(self, "stimulus", {str(k): float(v) for k, v in self.stimulus.items()})
        object.__setattr__(self, "available_actions", tuple(self.available_actions))
        object.__setattr__(self, "emission_state", dict(self.emission_state))
        object.__setattr__(self, "metadata", dict(self.metadata))


@dataclass(frozen=True)
class ConsequenceOutput:
    """Output of protocol-side consequence stage."""

    reward: float = 0.0
    done: bool = False
    outcome_state: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.outcome_state, dict):
            raise ValueError("ConsequenceOutput.outcome_state must be an object.")
        if not isinstance(self.metadata, dict):
            raise ValueError("ConsequenceOutput.metadata must be an object.")
        object.__setattr__(self, "reward", float(self.reward))
        object.__setattr__(self, "done", bool(self.done))
        object.__setattr__(self, "outcome_state", dict(self.outcome_state))
        object.__setattr__(self, "metadata", dict(self.metadata))


@dataclass(frozen=True)
class AdvanceOutput:
    """Output of protocol-side temporal advance stage."""

    t: int
    dt_s: float = 1.0
    phase_step: int = 0
    advance_state: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.advance_state, dict):
            raise ValueError("AdvanceOutput.advance_state must be an object.")
        if not isinstance(self.metadata, dict):
            raise ValueError("AdvanceOutput.metadata must be an object.")
        object.__setattr__(self, "t", int(self.t))
        object.__setattr__(self, "dt_s", float(self.dt_s))
        object.__setattr__(self, "phase_step", int(self.phase_step))
        object.__setattr__(self, "advance_state", dict(self.advance_state))
        object.__setattr__(self, "metadata", dict(self.metadata))


@dataclass(frozen=True)
class StopOutput:
    """Output of protocol-side stop-condition stage."""

    should_stop: bool
    reason: str | None = None
    stop_state: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.reason is not None and not isinstance(self.reason, str):
            raise ValueError("StopOutput.reason must be a string when provided.")
        if not isinstance(self.stop_state, dict):
            raise ValueError("StopOutput.stop_state must be an object.")
        if not isinstance(self.metadata, dict):
            raise ValueError("StopOutput.metadata must be an object.")
        object.__setattr__(self, "should_stop", bool(self.should_stop))
        object.__setattr__(self, "stop_state", dict(self.stop_state))
        object.__setattr__(self, "metadata", dict(self.metadata))


@dataclass(frozen=True)
class ProtocolStepResult:
    """Canonical protocol-stage aggregate for bundle execution."""

    emission: EmissionOutput
    consequence: ConsequenceOutput
    advance: AdvanceOutput
    stop: StopOutput
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.emission, EmissionOutput):
            raise ValueError("ProtocolStepResult.emission must be EmissionOutput.")
        if not isinstance(self.consequence, ConsequenceOutput):
            raise ValueError("ProtocolStepResult.consequence must be ConsequenceOutput.")
        if not isinstance(self.advance, AdvanceOutput):
            raise ValueError("ProtocolStepResult.advance must be AdvanceOutput.")
        if not isinstance(self.stop, StopOutput):
            raise ValueError("ProtocolStepResult.stop must be StopOutput.")
        if not isinstance(self.metadata, dict):
            raise ValueError("ProtocolStepResult.metadata must be an object.")
        object.__setattr__(self, "metadata", dict(self.metadata))
