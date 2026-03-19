"""Typed TrialState carrier for V3 environment semantics."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class TrialState:
    """
    Canonical trial-state coordinates:
    - s, x, z, w, a, u, y, m
    """

    s: Any
    x: Any
    z: Any
    w: Any
    a: Any
    u: Any
    y: Any
    m: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.m, dict):
            raise ValueError("TrialState.m must be an object.")

    def to_dict(self) -> dict[str, Any]:
        return {
            "s": self.s,
            "x": self.x,
            "z": self.z,
            "w": self.w,
            "a": self.a,
            "u": self.u,
            "y": self.y,
            "m": dict(self.m),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "TrialState":
        missing = [key for key in ("s", "x", "z", "w", "a", "u", "y", "m") if key not in data]
        if missing:
            joined = ", ".join(missing)
            raise ValueError(f"TrialState missing required coordinates: {joined}")
        return cls(
            s=data["s"],
            x=data["x"],
            z=data["z"],
            w=data["w"],
            a=data["a"],
            u=data["u"],
            y=data["y"],
            m=dict(data.get("m", {}) or {}),
        )
