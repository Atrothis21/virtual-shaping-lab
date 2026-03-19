"""V3 environment contracts (entry-criteria scaffolding for V3.3.0)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol, runtime_checkable


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
    metadata: dict[str, Any] = field(default_factory=dict)

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
            "metadata": dict(self.metadata),
        }


@runtime_checkable
class IEnvironment(Protocol):
    """Minimal environment stepping contract for V3 runtime migration."""

    def reset(self, *, seed: int | None = None) -> None: ...
    def step(self, action: Any = None) -> EnvironmentStep: ...
    @property
    def done(self) -> bool: ...
