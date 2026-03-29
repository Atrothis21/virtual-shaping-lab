"""Executable attention operators for learner core."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, MutableMapping

from .base import AttentionOperator


def _coerce_features(features: Mapping[str, float]) -> dict[str, float]:
    return {str(key): float(value) for key, value in features.items()}


def _coerce_attention_state(attention_state: MutableMapping[str, float] | None) -> dict[str, float]:
    if not isinstance(attention_state, Mapping):
        return {}
    return {str(key): float(value) for key, value in attention_state.items()}


def modulate_features_by_attention(
    *,
    features: Mapping[str, float],
    attention_state: Mapping[str, float] | None,
    default_gain: float = 1.0,
) -> dict[str, float]:
    """
    Apply attention gains to feature inputs.

    This helper intentionally modulates update inputs only. Error semantics
    remain independent of this transformation.
    """
    x = _coerce_features(features)
    gains = attention_state if isinstance(attention_state, Mapping) else {}
    out: dict[str, float] = {}
    base = float(default_gain)
    for key, value in x.items():
        out[key] = float(value) * float(gains.get(key, base))
    return out


@dataclass
class FixedAttentionOperator(AttentionOperator):
    """Static attention gains (default 1.0) for active features."""

    default_alpha: float = 1.0
    floor: float = 0.0
    ceiling: float = 1.0
    slot: str = "A"
    variant: str = "fixed_attention"

    def apply(
        self,
        *,
        attention_state: MutableMapping[str, float] | None,
        features: Mapping[str, float],
        error: float,
    ) -> MutableMapping[str, float] | None:
        _ = error
        state = _coerce_attention_state(attention_state)
        for key in _coerce_features(features).keys():
            if key not in state:
                state[key] = float(self.default_alpha)
            state[key] = min(float(self.ceiling), max(float(self.floor), float(state[key])))
        return state


@dataclass
class PearceHallAttentionOperator(AttentionOperator):
    """Pearce-Hall style unsigned error tracking per active feature."""

    default_alpha: float = 0.5
    kappa: float = 0.1
    floor: float = 0.0
    ceiling: float = 1.0
    slot: str = "A"
    variant: str = "pearce_hall"

    def apply(
        self,
        *,
        attention_state: MutableMapping[str, float] | None,
        features: Mapping[str, float],
        error: float,
    ) -> MutableMapping[str, float] | None:
        state = _coerce_attention_state(attention_state)
        target = abs(float(error))
        for key in _coerce_features(features).keys():
            current = float(state.get(key, float(self.default_alpha)))
            updated = current + float(self.kappa) * (target - current)
            state[key] = min(float(self.ceiling), max(float(self.floor), updated))
        return state


@dataclass
class MackintoshAttentionOperator(AttentionOperator):
    """Minimal Mackintosh-style relative predictiveness attention update."""

    default_alpha: float = 0.5
    kappa: float = 0.1
    floor: float = 0.0
    ceiling: float = 1.0
    slot: str = "A"
    variant: str = "mackintosh"

    def apply(
        self,
        *,
        attention_state: MutableMapping[str, float] | None,
        features: Mapping[str, float],
        error: float,
    ) -> MutableMapping[str, float] | None:
        state = _coerce_attention_state(attention_state)
        x = _coerce_features(features)
        if not x:
            return state
        magnitude = abs(float(error))
        scores = {key: abs(value) * magnitude for key, value in x.items()}
        mean_score = sum(scores.values()) / float(len(scores))

        for key in x.keys():
            current = float(state.get(key, float(self.default_alpha)))
            direction = 1.0 if scores[key] >= mean_score else -1.0
            updated = current + float(self.kappa) * direction
            state[key] = min(float(self.ceiling), max(float(self.floor), updated))
        return state

