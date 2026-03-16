# policies/epsilon_greedy.py

"""Epsilon-greedy policy for action selection."""

from __future__ import annotations

from typing import Any, Sequence

import numpy as np

from virtual_shaping_lab.agents.policies.base import Policy, ValueFn
from virtual_shaping_lab.domain.types import EncodedState


class EpsilonGreedyPolicy(Policy):
    """Epsilon-greedy action selection policy."""

    def __init__(
        self,
        actions: Sequence[Any] | None = None,
        epsilon: float = 0.1,
    ):
        self.actions = list(actions) if actions is not None else []
        self.epsilon = float(epsilon)

    def select_action(
        self,
        state: EncodedState,
        actions: Sequence[Any],
        value_fn: ValueFn,
        rng: np.random.Generator,
    ) -> Any:
        pool = list(actions) if actions else list(self.actions)
        if not pool:
            return None

        if float(rng.random()) < self.epsilon:
            idx = int(rng.integers(0, len(pool)))
            return pool[idx]

        values = [value_fn(state, action=a) for a in pool]
        best_idx = int(np.argmax(values))
        return pool[best_idx]

    def action_distribution(
        self,
        state: EncodedState,
        actions: Sequence[Any],
        value_fn: ValueFn,
    ) -> dict[Any, float]:
        pool = list(actions) if actions else list(self.actions)
        if not pool:
            return {}

        values = [value_fn(state, action=a) for a in pool]
        best_idx = int(np.argmax(values))
        n_actions = len(pool)
        base = self.epsilon / n_actions
        distribution = {action: base for action in pool}
        distribution[pool[best_idx]] += 1.0 - self.epsilon
        return distribution
