"""
Q-learning with linear function approximation.

Learns action-value functions:
    Q(s, a) = w_a^T s
"""

from typing import Dict, Optional, Sequence, Any
import numpy as np

from agents.learners.base import OperantLearner


class QLearner(OperantLearner):
    """
    Linear Q-learning learner.
    """

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

        # Weight matrix: (num_actions, state_dim)
        self.weights = np.zeros((len(self.actions), state_dim))

    def _action_index(self, action: Any) -> int:
        if action not in self.action_index:
            raise ValueError(f"Unknown action '{action}' for QLearner.")
        return self.action_index[action]

    def value(self, state: np.ndarray, action: Optional[Any] = None) -> float:
        """
        Return Q(s, a). If action is None, return max_a Q(s, a).
        """
        if action is None:
            return float(np.max(self.weights @ state))
        idx = self._action_index(action)
        return float(np.dot(self.weights[idx], state))

    def update(
        self,
        state: np.ndarray,
        reward: float,
        action: Optional[Any] = None,
        next_state: Optional[np.ndarray] = None,
        done: Optional[bool] = None
    ) -> None:
        """
        Q-learning update rule.
        """
        if action is None:
            raise ValueError("QLearner.update requires an action")

        a_idx = self._action_index(action)
        q_sa = float(np.dot(self.weights[a_idx], state))

        if next_state is None or done:
            q_next = 0.0
        else:
            q_next = float(np.max(self.weights @ next_state))

        td_error = reward + self.gamma * q_next - q_sa

        self.weights[a_idx] += self.alpha * td_error * state

    def update_with_alpha(self, state, reward, action=None, alpha_override=None, delta_override=None):
        if action is None:
            return  # cannot update Q-values without action

        a_idx = self._action_index(action)
        q = self.value(state, action)
        delta = delta_override if delta_override is not None else (reward - q)
        alpha = self.alpha if alpha_override is None else alpha_override

        self.weights[a_idx] += alpha * delta * state

    def get_parameters(self) -> Dict[str, np.ndarray]:
        return {"weights": self.weights.copy()}

