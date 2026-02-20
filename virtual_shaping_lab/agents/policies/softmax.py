# policies/softmax.py

"""
Softmax (Boltzmann) action selection policy.
"""

from typing import Any, Sequence
import numpy as np

from agents.policies.base import Policy, ValueFn


class SoftmaxPolicy(Policy):
    """
    Softmax action selection based on action values.
    """

    def __init__(
        self,
        actions: Sequence[Any],
        temperature: float = 1.0,
    ):
        self.actions = list(actions)
        self.temperature = temperature

    def select_action(self, state: np.ndarray, value_fn: ValueFn) -> Any:
        values = np.array(
            [value_fn(state, action=a) for a in self.actions],
            dtype=float
        )

        # Numerical stability
        values -= np.max(values)

        # Avoid divide-by-zero if temperature is 0 or tiny
        temp = self.temperature if self.temperature > 0 else 1e-8

        probs = np.exp(values / temp)
        probs /= np.sum(probs)

        return np.random.choice(self.actions, p=probs)

