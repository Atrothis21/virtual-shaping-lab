"""Concrete prediction-error rule objects for learner updates."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

import numpy as np

from virtual_shaping_lab.agents.math_objects.interfaces import IPredictionErrorRule


@dataclass(frozen=True)
class RescorlaWagnerPredictionError(IPredictionErrorRule):
    """Rescorla-Wagner residual.

    Domain/codomain:
    - maps `(x_t, r_t, x_{t+1}, theta_t, metadata)` to a scalar prediction error
    - formal shape: `delta_t = r_t - y_hat_t`
    """

    def compute(
        self,
        *,
        state: np.ndarray,
        reward: float,
        next_state: np.ndarray | None = None,
        parameters: Any = None,
        metadata: Mapping[str, Any] | None = None,
    ) -> float:
        weights = np.asarray(parameters, dtype=float)
        x_t = np.asarray(state, dtype=float)
        prediction = float(np.dot(weights, x_t))
        return float(reward) - prediction


@dataclass(frozen=True)
class TD0PredictionError(IPredictionErrorRule):
    """TD(0) residual.

    Domain/codomain:
    - maps `(x_t, r_t, x_{t+1}, theta_t, metadata)` to a scalar prediction error
    - formal shape: `delta_t = r_t + gamma V(x_{t+1}) - V(x_t)`
    """

    gamma: float = 0.0

    def compute(
        self,
        *,
        state: np.ndarray,
        reward: float,
        next_state: np.ndarray | None = None,
        parameters: Any = None,
        metadata: Mapping[str, Any] | None = None,
    ) -> float:
        weights = np.asarray(parameters, dtype=float)
        x_t = np.asarray(state, dtype=float)
        v_t = float(np.dot(weights, x_t))
        if next_state is None:
            v_next = 0.0
        else:
            v_next = float(np.dot(weights, np.asarray(next_state, dtype=float)))
        return float(reward) + float(self.gamma) * v_next - v_t

