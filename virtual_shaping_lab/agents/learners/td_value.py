# learners/td_value.py

from __future__ import annotations

from typing import Optional, Any

import numpy as np

from virtual_shaping_lab.agents.math_objects.interfaces import IAttentionMechanism, IPredictionErrorRule
from virtual_shaping_lab.agents.math_objects.prediction_error_objects import TD0PredictionError
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
        prediction_error_rule: IPredictionErrorRule | None = None,
        attention_mechanism: IAttentionMechanism | None = None,
    ):
        super().__init__(alpha=alpha, gamma=gamma, attention_mechanism=attention_mechanism)
        self.weights = np.zeros(state_dim, dtype=float)
        self.salience = None if salience is None else np.asarray(salience, dtype=float)
        self.prediction_error_rule = prediction_error_rule or TD0PredictionError(gamma=float(gamma))

    def value(self, state: EncodedState, action: Any = None) -> float:
        return float(np.dot(self.weights, state.x))

    def update(self, transition: Transition) -> None:
        v = self.value(transition.s)
        next_state = None if transition.s_next is None or transition.done else transition.s_next.x
        delta = self.prediction_error_rule.compute(
            state=transition.s.x,
            reward=transition.r,
            next_state=next_state,
            parameters=self.weights,
            metadata=transition.metadata,
        )
        x_mod = self.attention_modulated_state(
            transition,
            total_prediction=v,
            prediction_error=delta,
            feature_contributions=self.feature_contributions_for_transition(
                transition,
                self.weights,
            ),
        )
        self.weights += float(self.alpha) * float(delta) * x_mod

    def get_parameters(self):
        return {"weights": self.weights.copy()}

