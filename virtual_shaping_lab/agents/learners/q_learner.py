"""Q-learning with linear function approximation over EncodedState."""

from __future__ import annotations

from typing import Dict, Optional, Sequence, Any

import numpy as np

from virtual_shaping_lab.agents.learners.base import OperantLearner
from virtual_shaping_lab.domain.types import EncodedState, Transition


class QLearner(OperantLearner):
    """Linear Q-learning learner."""

    name = "q_learner"
    learner_type = "operant"

    def __init__(
        self,
        state_dim: int,
        actions: Sequence[Any],
        alpha: float = 0.1,
        gamma: float = 0.9,
        salience: Optional[np.ndarray] = None,
    ):
        super().__init__(alpha=alpha, gamma=gamma)
        self.actions = list(actions)
        self.action_index = {a: i for i, a in enumerate(self.actions)}
        self.salience = None if salience is None else np.asarray(salience, dtype=float)
        self.weights = np.zeros((len(self.actions), state_dim), dtype=float)

    def _action_index(self, action: Any) -> int:
        if action not in self.action_index:
            raise ValueError(f"Unknown action '{action}' for QLearner.")
        return self.action_index[action]

    def value(self, state: EncodedState, action: Optional[Any] = None) -> float:
        x = state.x
        if action is None:
            return float(np.max(self.weights @ x))
        idx = self._action_index(action)
        return float(np.dot(self.weights[idx], x))

    def update(self, transition: Transition) -> None:
        action = transition.a
        if action is None:
            raise ValueError("QLearner.update requires transition.a")

        a_idx = self._action_index(action)
        q_sa = float(np.dot(self.weights[a_idx], transition.s.x))

        if transition.s_next is None or transition.done:
            q_next = 0.0
        else:
            q_next = float(np.max(self.weights @ transition.s_next.x))

        delta = transition.metadata.get("delta_override")
        if delta is None:
            delta = transition.r + self.gamma * q_next - q_sa

        alpha = transition.metadata.get("alpha_override")
        alpha = self.alpha if alpha is None else float(alpha)

        self.weights[a_idx] += alpha * float(delta) * transition.s.x

    def get_parameters(self) -> Dict[str, np.ndarray]:
        return {"weights": self.weights.copy()}
