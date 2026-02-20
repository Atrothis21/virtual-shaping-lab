# learners/rescorla_wagner.py

from typing import Optional
import numpy as np

from agents.learners.base import BaseLearner


class RescorlaWagnerLearner(BaseLearner):
    """
    Linear Rescorla-Wagner learner over a vector representation.

    Update rule:
        delta = reward - prediction
        w += alpha * delta * (salience * state)
    """

    name = "rescorla_wagner"
    learner_type = "pavlovian"

    def __init__(
        self,
        state_dim: int,
        alpha: float = 0.1,
        gamma: float = 0.0,
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
        prediction = self.value(state)
        delta = reward - prediction

        if self.salience is None:
            self.weights += self.alpha * delta * state
        else:
            self.weights += self.alpha * delta * (self.salience * state)
    
    def update_with_alpha(self, state, reward, action=None, alpha_override=None, delta_override=None):
        prediction = self.value(state)
        delta = delta_override if delta_override is not None else (reward - prediction)
        alpha = self.alpha if alpha_override is None else alpha_override

        if self.salience is not None:
            self.weights += alpha * delta * (self.salience * state)
        else:
            self.weights += alpha * delta * state



