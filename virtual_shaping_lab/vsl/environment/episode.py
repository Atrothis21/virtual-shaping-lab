"""Typed runtime episode and horizon contracts for V3."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any


def _normalize_mapping(value: Any, field_name: str) -> dict[str, Any]:
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise ValueError(f"{field_name} must be an object.")
    return dict(value)


@dataclass(frozen=True)
class TerminationCondition:
    """Typed terminal-state contract for episode completion semantics."""

    reason: str
    terminal: bool
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        reason = str(self.reason or "").strip()
        if not reason:
            raise ValueError("TerminationCondition.reason must be a non-empty string.")
        object.__setattr__(self, "reason", reason)
        object.__setattr__(self, "terminal", bool(self.terminal))
        object.__setattr__(self, "metadata", _normalize_mapping(self.metadata, "TerminationCondition.metadata"))

    def to_dict(self) -> dict[str, Any]:
        return {
            "reason": self.reason,
            "terminal": bool(self.terminal),
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "TerminationCondition":
        return cls(
            reason=data.get("reason", ""),
            terminal=bool(data.get("terminal", False)),
            metadata=data.get("metadata", {}),
        )


@dataclass(frozen=True)
class HorizonSpec:
    """Typed horizon bounds for runtime episode stepping."""

    max_steps: int | None = None
    max_duration_s: float | None = None
    stop_reason: str = "horizon_exhausted"

    def __post_init__(self) -> None:
        max_steps = self.max_steps
        if max_steps is not None:
            max_steps = int(max_steps)
            if max_steps <= 0:
                raise ValueError("HorizonSpec.max_steps must be > 0 when provided.")
        max_duration_s = self.max_duration_s
        if max_duration_s is not None:
            max_duration_s = float(max_duration_s)
            if max_duration_s <= 0.0:
                raise ValueError("HorizonSpec.max_duration_s must be > 0 when provided.")
        if max_steps is None and max_duration_s is None:
            raise ValueError("HorizonSpec requires max_steps and/or max_duration_s.")
        stop_reason = str(self.stop_reason or "").strip()
        if not stop_reason:
            raise ValueError("HorizonSpec.stop_reason must be a non-empty string.")
        object.__setattr__(self, "max_steps", max_steps)
        object.__setattr__(self, "max_duration_s", max_duration_s)
        object.__setattr__(self, "stop_reason", stop_reason)

    def to_dict(self) -> dict[str, Any]:
        return {
            "max_steps": self.max_steps,
            "max_duration_s": self.max_duration_s,
            "stop_reason": self.stop_reason,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "HorizonSpec":
        return cls(
            max_steps=data.get("max_steps"),
            max_duration_s=data.get("max_duration_s"),
            stop_reason=data.get("stop_reason", "horizon_exhausted"),
        )


@dataclass(frozen=True)
class EpisodeSpec:
    """Typed episode identity and horizon declaration."""

    episode_id: int
    rollout_id: str
    seed: int | None = None
    horizon: HorizonSpec = field(default_factory=lambda: HorizonSpec(max_steps=1))
    termination: TerminationCondition = field(
        default_factory=lambda: TerminationCondition(reason="running", terminal=False)
    )

    def __post_init__(self) -> None:
        episode_id = int(self.episode_id)
        if episode_id < 0:
            raise ValueError("EpisodeSpec.episode_id must be >= 0.")
        rollout_id = str(self.rollout_id or "").strip()
        if not rollout_id:
            raise ValueError("EpisodeSpec.rollout_id must be a non-empty string.")
        seed = self.seed
        if seed is not None:
            seed = int(seed)
        if not isinstance(self.horizon, HorizonSpec):
            raise ValueError("EpisodeSpec.horizon must be a HorizonSpec.")
        if not isinstance(self.termination, TerminationCondition):
            raise ValueError("EpisodeSpec.termination must be a TerminationCondition.")
        object.__setattr__(self, "episode_id", episode_id)
        object.__setattr__(self, "rollout_id", rollout_id)
        object.__setattr__(self, "seed", seed)

    def to_dict(self) -> dict[str, Any]:
        return {
            "episode_id": self.episode_id,
            "rollout_id": self.rollout_id,
            "seed": self.seed,
            "horizon": self.horizon.to_dict(),
            "termination": self.termination.to_dict(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "EpisodeSpec":
        return cls(
            episode_id=int(data.get("episode_id", 0)),
            rollout_id=data.get("rollout_id", ""),
            seed=data.get("seed"),
            horizon=HorizonSpec.from_dict(data.get("horizon", {})),
            termination=TerminationCondition.from_dict(
                data.get("termination", {"reason": "running", "terminal": False, "metadata": {}})
            ),
        )

    def stable_hash(self) -> str:
        blob = json.dumps(self.to_dict(), sort_keys=True, separators=(",", ":")).encode("utf-8")
        return hashlib.sha256(blob).hexdigest()

