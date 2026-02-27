# learners/td_value.py

from __future__ import annotations

from typing import Optional, Any

import numpy as np

from virtual_shaping_lab.agents.learners.base import BaseLearner
from virtual_shaping_lab.domain.types import EncodedState, Transition


class TDValueLearner(BaseLearner):
    """TD(0) value learner over vectorized EncodedState."""

    name = "td_value"
    learner_type = "pavlovian"

    def __init__(
        self,
        state_dim: int,
        alpha: float = 0.1,
        gamma: float = 0.9,
        salience: Optional[np.ndarray] = None,
    ):
        super().__init__(alpha=alpha, gamma=gamma)
        self.weights = np.zeros(state_dim, dtype=float)
        self.salience = None if salience is None else np.asarray(salience, dtype=float)

    def value(self, state: EncodedState, action: Any = None) -> float:
        return float(np.dot(self.weights, state.x))

    def update(self, transition: Transition) -> None:
        v = self.value(transition.s)

        if transition.s_next is None or transition.done:
            v_next = 0.0
        else:
            v_next = self.value(transition.s_next)

        delta = transition.r + self.gamma * v_next - v
        alpha = self.alpha

        self.weights += alpha * float(delta) * transition.s.x

    def update_with_alpha(
        self,
        state: EncodedState,
        reward: float,
        action: Any = None,
        alpha_override: Optional[float] = None,
        delta_override: Optional[float] = None,
        next_state: Optional[EncodedState] = None,
        done: bool = False,
        t_s: Optional[float] = None,
        dt_s: Optional[float] = None,
    ) -> None:
        prediction = self.value(state)
        delta = (reward - prediction) if delta_override is None else float(delta_override)
        alpha = self.alpha if alpha_override is None else float(alpha_override)
        self.weights += alpha * delta * state.x

    def get_parameters(self):
        return {"weights": self.weights.copy()}

