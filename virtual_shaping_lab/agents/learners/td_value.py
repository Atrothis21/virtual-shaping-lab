# learners/td_value.py

from typing import Optional
import numpy as np

from agents.learners.base import BaseLearner


class TDValueLearner(BaseLearner):
    """
    TD(0) value learner over a vector representation.

    Learns V(s) only (Pavlovian).
    """

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

    def value(self, state: np.ndarray, action: Optional[int] = None) -> float:
        return float(np.dot(self.weights, state))

    def update(
        self,
        state: np.ndarray,
        reward: float,
        action: Optional[int] = None,
        next_state: Optional[np.ndarray] = None,
        done: Optional[bool] = None
    ) -> None:
        v = self.value(state)
        v_next = 0.0
        if next_state is not None and not done:
            v_next = self.value(next_state)

        delta = reward + self.gamma * v_next - v

        self.weights += self.alpha * delta * state
    
    def update_with_alpha(self, state, reward, action=None, alpha_override=None, delta_override=None):
        prediction = self.value(state)
        delta = delta_override if delta_override is not None else (reward - prediction)
        alpha = self.alpha if alpha_override is None else alpha_override

        self.weights += alpha * delta * state



