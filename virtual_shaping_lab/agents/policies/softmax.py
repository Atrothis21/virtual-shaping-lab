# policies/softmax.py

"""Softmax (Boltzmann) action selection policy."""

from __future__ import annotations

from typing import Any, Sequence

import numpy as np

from virtual_shaping_lab.agents.policies.base import Policy, ValueFn
from virtual_shaping_lab.domain.types import EncodedState


class SoftmaxPolicy(Policy):
    """Softmax action selection based on action values."""

    def __init__(
        self,
        actions: Sequence[Any] | None = None,
        temperature: float = 1.0,
    ):
        self.actions = list(actions) if actions is not None else []
        self.temperature = float(temperature)

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

        values = np.array([value_fn(state, action=a) for a in pool], dtype=float)
        values -= np.max(values)

        temp = self.temperature if self.temperature > 0 else 1e-8
        probs = np.exp(values / temp)
        probs /= np.sum(probs)

        idx = int(rng.choice(len(pool), p=probs))
        return pool[idx]

    def action_distribution(
        self,
        state: EncodedState,
        actions: Sequence[Any],
        value_fn: ValueFn,
    ) -> dict[Any, float]:
        pool = list(actions) if actions else list(self.actions)
        if not pool:
            return {}

        values = np.array([value_fn(state, action=a) for a in pool], dtype=float)
        values -= np.max(values)

        temp = self.temperature if self.temperature > 0 else 1e-8
        probs = np.exp(values / temp)
        probs /= np.sum(probs)
        return {action: float(prob) for action, prob in zip(pool, probs)}
