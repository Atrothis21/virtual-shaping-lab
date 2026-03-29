"""Update operators for executable learner core."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, MutableMapping

from .base import UpdateOperator


def _coerce_features(features: Mapping[str, float]) -> dict[str, float]:
    return {str(k): float(v) for k, v in features.items()}


def _coerce_weights(raw: Any) -> dict[str, float]:
    if not isinstance(raw, Mapping):
        return {}
    return {str(k): float(v) for k, v in raw.items()}


@dataclass
class RescorlaWagnerUpdateOperator(UpdateOperator):
    """Linear RW update over feature weights: w <- w + alpha*delta*x."""

    weights_key: str = "weights"

    def __call__(
        self,
        *,
        state: MutableMapping[str, Any],
        features: Mapping[str, float],
        error: float,
        step_size: float,
    ) -> MutableMapping[str, Any]:
        x = _coerce_features(features)
        weights = _coerce_weights(state.get(self.weights_key))
        alpha_delta = float(step_size) * float(error)
        for key, value in x.items():
            weights[key] = float(weights.get(key, 0.0)) + alpha_delta * value
        state[self.weights_key] = weights
        return state


@dataclass
class TD0UpdateOperator(UpdateOperator):
    """Linear TD(0) update over feature weights: w <- w + alpha*delta*x."""

    weights_key: str = "weights"

    def __call__(
        self,
        *,
        state: MutableMapping[str, Any],
        features: Mapping[str, float],
        error: float,
        step_size: float,
    ) -> MutableMapping[str, Any]:
        x = _coerce_features(features)
        weights = _coerce_weights(state.get(self.weights_key))
        alpha_delta = float(step_size) * float(error)
        for key, value in x.items():
            weights[key] = float(weights.get(key, 0.0)) + alpha_delta * value
        state[self.weights_key] = weights
        return state

