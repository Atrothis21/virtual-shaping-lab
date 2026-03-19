"""V3 environment contracts (entry-criteria scaffolding for V3.3.0)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol, runtime_checkable

from virtual_shaping_lab.vsl.environment.trial_state import TrialState


@dataclass(frozen=True)
class EnvironmentReset:
    """Typed reset result emitted when an environment is reset."""

    seed: int | None = None
    done: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.seed is not None and not isinstance(self.seed, int):
            raise ValueError("EnvironmentReset.seed must be an int when provided.")
        if not isinstance(self.done, bool):
            raise ValueError("EnvironmentReset.done must be a bool.")
        if not isinstance(self.metadata, dict):
            raise ValueError("EnvironmentReset.metadata must be an object.")

    def to_dict(self) -> dict[str, Any]:
        return {
            "seed": self.seed,
            "done": self.done,
            "metadata": dict(self.metadata),
        }


@dataclass(frozen=True)
class EnvironmentTermination:
    """Typed terminal-state descriptor for environment stepping."""

    done: bool
    reason: str = "running"
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.done, bool):
            raise ValueError("EnvironmentTermination.done must be a bool.")
        if not isinstance(self.reason, str) or not self.reason.strip():
            raise ValueError("EnvironmentTermination.reason must be a non-empty string.")
        if not isinstance(self.metadata, dict):
            raise ValueError("EnvironmentTermination.metadata must be an object.")

    def to_dict(self) -> dict[str, Any]:
        return {
            "done": self.done,
            "reason": self.reason,
            "metadata": dict(self.metadata),
        }


@dataclass(frozen=True)
class EnvironmentStep:
    """Normalized output emitted by environment stepping."""

    step_index: int
    segment_key: str
    protocol: str
    trial_type: str
    trial_index: int
    action: Any
    stimulus: dict[str, Any] = field(default_factory=dict)
    reward: float = 0.0
    done: bool = False
    trial_state: TrialState | None = None
    termination: EnvironmentTermination = field(default_factory=lambda: EnvironmentTermination(done=False))
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if int(self.step_index) < 0:
            raise ValueError("EnvironmentStep.step_index must be >= 0.")
        if not isinstance(self.segment_key, str) or not self.segment_key.strip():
            raise ValueError("EnvironmentStep.segment_key must be a non-empty string.")
        if not isinstance(self.protocol, str) or not self.protocol.strip():
            raise ValueError("EnvironmentStep.protocol must be a non-empty string.")
        if not isinstance(self.trial_type, str) or not self.trial_type.strip():
            raise ValueError("EnvironmentStep.trial_type must be a non-empty string.")
        if int(self.trial_index) < 0:
            raise ValueError("EnvironmentStep.trial_index must be >= 0.")
        if not isinstance(self.stimulus, dict):
            raise ValueError("EnvironmentStep.stimulus must be an object.")
        if not isinstance(self.done, bool):
            raise ValueError("EnvironmentStep.done must be a bool.")
        if self.trial_state is not None and not isinstance(self.trial_state, TrialState):
            raise ValueError("EnvironmentStep.trial_state must be a TrialState when provided.")
        if not isinstance(self.termination, EnvironmentTermination):
            raise ValueError("EnvironmentStep.termination must be an EnvironmentTermination.")
        if not isinstance(self.metadata, dict):
            raise ValueError("EnvironmentStep.metadata must be an object.")

    def to_dict(self) -> dict[str, Any]:
        return {
            "step_index": int(self.step_index),
            "segment_key": self.segment_key,
            "protocol": self.protocol,
            "trial_type": self.trial_type,
            "trial_index": int(self.trial_index),
            "action": self.action,
            "stimulus": dict(self.stimulus),
            "reward": float(self.reward),
            "done": bool(self.done),
            "trial_state": None if self.trial_state is None else self.trial_state.to_dict(),
            "termination": self.termination.to_dict(),
            "metadata": dict(self.metadata),
        }


@runtime_checkable
class IEnvironment(Protocol):
    """Minimal environment stepping contract for V3 runtime migration."""

    def reset(self, *, seed: int | None = None) -> EnvironmentReset: ...
    def step(self, action: Any = None) -> EnvironmentStep: ...
    @property
    def done(self) -> bool: ...
