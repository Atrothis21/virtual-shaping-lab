"""Learner-owned attention strategy contracts and baseline implementations."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, Protocol


@dataclass(frozen=True)
class AttentionContext:
    """Required sufficient statistics for attention strategy state updates."""

    active_features: tuple[str, ...]
    feature_contributions: Mapping[str, float]
    total_prediction: float
    reward: float
    prediction_error: float


def _normalize_overrides(overrides: Mapping[str, Any] | None) -> dict[str, float]:
    if not isinstance(overrides, Mapping):
        return {}
    out: dict[str, float] = {}
    for key, value in overrides.items():
        try:
            out[str(key)] = float(value)
        except (TypeError, ValueError):
            continue
    return out


def _as_labels(cue_labels: Any) -> list[str]:
    if cue_labels is None:
        return []
    if isinstance(cue_labels, (str, int, float)):
        return [str(cue_labels)]
    return [str(label) for label in cue_labels]


def _clip01(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


@dataclass
class AttentionState:
    """Internal learner-owned attention state."""

    default: float = 1.0
    overrides: dict[str, float] = field(default_factory=dict)
    alpha_by_feature: dict[str, float] = field(default_factory=dict)


class AttentionStrategy(Protocol):
    """Behavioral contract for attention strategies."""

    name: str

    def reset(self) -> None:
        ...

    def current_alpha(self, active_features: tuple[str, ...]) -> dict[str, float]:
        ...

    def current_alpha_for_cues(self, cue_labels: Any) -> float:
        ...

    def update_state(self, context: AttentionContext) -> AttentionState:
        ...


class BaseAttentionStrategy:
    """Shared mechanics for stateful attention strategies."""

    name = "none"

    def __init__(self, *, default: float = 1.0, overrides: Mapping[str, Any] | None = None):
        self._state = AttentionState(
            default=_clip01(float(default)),
            overrides={k: _clip01(v) for k, v in _normalize_overrides(overrides).items()},
            alpha_by_feature={},
        )

    def reset(self) -> None:
        self._state.alpha_by_feature = {}

    def current_alpha(self, active_features: tuple[str, ...]) -> dict[str, float]:
        return {
            feature: self._alpha_for_feature(feature)
            for feature in active_features
        }

    def current_alpha_for_cues(self, cue_labels: Any) -> float:
        labels = _as_labels(cue_labels)
        if not labels:
            return float(self._state.default)
        vals = [self._alpha_for_feature(label) for label in labels]
        return sum(vals) / len(vals)

    def _alpha_for_feature(self, feature: str) -> float:
        if feature in self._state.alpha_by_feature:
            return _clip01(self._state.alpha_by_feature[feature])
        if feature in self._state.overrides:
            return _clip01(self._state.overrides[feature])
        return _clip01(self._state.default)

    def update_state(self, context: AttentionContext) -> AttentionState:
        self._state.alpha_by_feature = self.current_alpha(tuple(context.active_features))
        return self._state


class NoAttentionStrategy(BaseAttentionStrategy):
    """No modulation baseline: all cues use alpha multiplier 1.0."""

    name = "none"

    def __init__(self) -> None:
        super().__init__(default=1.0, overrides={})


class StaticAttentionStrategy(BaseAttentionStrategy):
    """Static per-cue overrides without dynamical updates."""

    name = "static"


class PearceHallAttentionStrategy(BaseAttentionStrategy):
    """Surprise-driven associability updates for active cues."""

    name = "pearce_hall"

    def __init__(
        self,
        *,
        default: float = 0.5,
        overrides: Mapping[str, Any] | None = None,
        eta: float = 0.2,
    ):
        super().__init__(default=default, overrides=overrides)
        self._eta = _clip01(eta)

    def update_state(self, context: AttentionContext) -> AttentionState:
        target = _clip01(abs(context.prediction_error))
        active = tuple(str(f) for f in context.active_features)
        if not active:
            self._state.alpha_by_feature = {}
            return self._state

        updated: dict[str, float] = dict(self._state.alpha_by_feature)
        for feature in active:
            prev = self._alpha_for_feature(feature)
            updated[feature] = _clip01((1.0 - self._eta) * prev + self._eta * target)
        self._state.alpha_by_feature = updated
        return self._state


class MackintoshAttentionStrategy(BaseAttentionStrategy):
    """Relative predictiveness updates based on cuewise contribution contrast."""

    name = "mackintosh"

    def __init__(
        self,
        *,
        default: float = 0.5,
        overrides: Mapping[str, Any] | None = None,
        kappa: float = 0.1,
    ):
        super().__init__(default=default, overrides=overrides)
        self._kappa = _clip01(kappa)

    def update_state(self, context: AttentionContext) -> AttentionState:
        active = tuple(str(f) for f in context.active_features)
        if not active:
            self._state.alpha_by_feature = {}
            return self._state

        contributions = {
            str(k): abs(float(v))
            for k, v in context.feature_contributions.items()
            if str(k) in active
        }
        updated: dict[str, float] = dict(self._state.alpha_by_feature)
        for feature in active:
            own = contributions.get(feature, 0.0)
            others = [v for k, v in contributions.items() if k != feature]
            other_mean = (sum(others) / len(others)) if others else 0.0
            prev = self._alpha_for_feature(feature)
            if own >= other_mean:
                next_alpha = prev + self._kappa * (1.0 - prev)
            else:
                next_alpha = prev - self._kappa * prev
            updated[feature] = _clip01(next_alpha)
        self._state.alpha_by_feature = updated
        return self._state


def build_attention_strategy(name: str, *, params: Mapping[str, Any] | None = None) -> AttentionStrategy:
    normalized = str(name or "none").strip().lower()
    params = params if isinstance(params, Mapping) else {}
    if normalized == "none":
        return NoAttentionStrategy()
    if normalized == "static":
        return StaticAttentionStrategy(
            default=float(params.get("default", 1.0)),
            overrides=params.get("overrides", {}),
        )
    if normalized == "pearce_hall":
        return PearceHallAttentionStrategy(
            default=float(params.get("default", 0.5)),
            overrides=params.get("overrides", {}),
            eta=float(params.get("eta", 0.2)),
        )
    if normalized == "mackintosh":
        return MackintoshAttentionStrategy(
            default=float(params.get("default", 0.5)),
            overrides=params.get("overrides", {}),
            kappa=float(params.get("kappa", 0.1)),
        )
    raise ValueError(f"Unsupported attention strategy '{name}'")
