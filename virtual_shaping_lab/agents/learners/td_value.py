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

        delta = transition.metadata.get("delta_override")
        if delta is None:
            delta = transition.r + self.gamma * v_next - v

        alpha = transition.metadata.get("alpha_override")
        alpha = self.alpha if alpha is None else float(alpha)

        self.weights += alpha * float(delta) * transition.s.x

    def get_parameters(self):
        return {"weights": self.weights.copy()}
