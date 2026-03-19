"""Typed TrialState carrier for V3 environment semantics."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

_DERIVED_KEYS = {"prediction", "error"}
_META_PERSISTENT_KEY = "persistent"
_META_DERIVED_KEY = "derived"


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
        persistent = self.m.get(_META_PERSISTENT_KEY, {})
        derived = self.m.get(_META_DERIVED_KEY, {})
        if not isinstance(persistent, dict):
            raise ValueError("TrialState.m.persistent must be an object when provided.")
        if not isinstance(derived, dict):
            raise ValueError("TrialState.m.derived must be an object when provided.")
        leaked = sorted(_DERIVED_KEYS.intersection(persistent.keys()))
        if leaked:
            leaked_str = ", ".join(leaked)
            raise ValueError(f"TrialState.m.persistent must not contain derived outputs: {leaked_str}")
        invalid_derived = sorted(set(derived.keys()) - _DERIVED_KEYS)
        if invalid_derived:
            invalid_str = ", ".join(invalid_derived)
            raise ValueError(
                f"TrialState.m.derived may only contain derived outputs ({', '.join(sorted(_DERIVED_KEYS))}); found: {invalid_str}"
            )

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
    def from_components(
        cls,
        *,
        s: Any,
        x: Any,
        z: Any,
        w: Any,
        a: Any,
        u: Any,
        y: Any,
        persistent: dict[str, Any] | None = None,
        prediction: Any = None,
        error: Any = None,
    ) -> "TrialState":
        derived: dict[str, Any] = {}
        if prediction is not None:
            derived["prediction"] = prediction
        if error is not None:
            derived["error"] = error
        return cls(
            s=s,
            x=x,
            z=z,
            w=w,
            a=a,
            u=u,
            y=y,
            m={
                _META_PERSISTENT_KEY: dict(persistent or {}),
                _META_DERIVED_KEY: derived,
            },
        )

    def persistent_metadata(self) -> dict[str, Any]:
        return dict(self.m.get(_META_PERSISTENT_KEY, {}) or {})

    def derived_outputs(self) -> dict[str, Any]:
        return dict(self.m.get(_META_DERIVED_KEY, {}) or {})

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
