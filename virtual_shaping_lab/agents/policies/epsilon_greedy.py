# policies/epsilon_greedy.py

"""
Epsilon-greedy policy for action selection.
"""

from typing import Any, Sequence
import numpy as np
import random

from agents.policies.base import Policy, ValueFn


class EpsilonGreedyPolicy(Policy):
    """
    Epsilon-greedy action selection policy.
    """

    def __init__(
        self,
        actions: Sequence[Any],
        epsilon: float = 0.1,
    ):
        """
        Parameters
        ----------
        actions : sequence
            Available actions
        epsilon : float
            Probability of random action
        """
        self.actions = list(actions)
        self.epsilon = epsilon

    def select_action(self, state: np.ndarray, value_fn: ValueFn) -> Any:
        """
        Choose an action using epsilon-greedy strategy.
        """
        if random.random() < self.epsilon:
            return random.choice(self.actions)

        # Exploit: choose best action according to value_fn
        values = [value_fn(state, action=a) for a in self.actions]
        best_idx = int(np.argmax(values))
        return self.actions[best_idx]

