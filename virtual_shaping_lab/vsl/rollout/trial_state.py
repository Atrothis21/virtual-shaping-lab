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
    - s, x, z, w, attention_state, a, u, y, m
    """

    s: Any
    x: Any
    z: Any
    w: Any
    a: Any
    u: Any
    y: Any
    attention_state: Any = None
    m: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.m, dict):
            raise ValueError("TrialState.m must be an object.")
        if not isinstance(self.a, list):
            raise ValueError("TrialState.a must be a list.")
        if len(self.a) == 1 and self.a[0] is None and self.u is not None:
            raise ValueError("TrialState classical null-action shape requires u=None when a=[None].")
        if self.u is not None and len(self.a) == 0:
            raise ValueError("TrialState requires non-empty action support list when u is set.")
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
            "attention_state": self.attention_state,
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
        attention_state: Any = None,
        persistent: dict[str, Any] | None = None,
        prediction: Any = None,
        error: Any = None,
    ) -> "TrialState":
        # Keep derived schema stable across records by always emitting both keys.
        derived: dict[str, Any] = {
            "prediction": prediction,
            "error": error,
        }
        return cls(
            s=s,
            x=x,
            z=z,
            w=w,
            attention_state=attention_state,
            a=a,
            u=u,
            y=y,
            m={
                _META_PERSISTENT_KEY: dict(persistent or {}),
                _META_DERIVED_KEY: derived,
            },
        )

    @classmethod
    def with_action_semantics(
        cls,
        *,
        s: Any,
        x: Any,
        z: Any,
        w: Any,
        y: Any,
        is_operant: bool,
        attention_state: Any = None,
        action: Any = None,
        available_actions: list[Any] | None = None,
        persistent: dict[str, Any] | None = None,
        prediction: Any = None,
        error: Any = None,
    ) -> "TrialState":
        if is_operant:
            action_space = list(available_actions or [])
            if action is not None and action not in action_space:
                action_space = [*action_space, action]
            return cls.from_components(
                s=s,
                x=x,
                z=z,
                w=w,
                attention_state=attention_state,
                a=action_space,
                u=action,
                y=y,
                persistent=persistent,
                prediction=prediction,
                error=error,
            )

        return cls.from_components(
            s=s,
            x=x,
            z=z,
            w=w,
            attention_state=attention_state,
            a=[None],
            u=None,
            y=y,
            persistent=persistent,
            prediction=prediction,
            error=error,
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
        # Backward-compat adapter (one-release window):
        # accept legacy "attention" payload key and normalize to "attention_state".
        attention_state = data.get("attention_state", data.get("attention"))
        return cls(
            s=data["s"],
            x=data["x"],
            z=data["z"],
            w=data["w"],
            attention_state=attention_state,
            a=data["a"],
            u=data["u"],
            y=data["y"],
            m=dict(data.get("m", {}) or {}),
        )
