# policies/fixed_policy.py

"""Fixed policy for classical conditioning or control experiments."""

from __future__ import annotations

from typing import Any, Sequence

import numpy as np

from virtual_shaping_lab.agents.policies.base import Policy, ValueFn
from virtual_shaping_lab.domain.types import EncodedState


class FixedPolicy(Policy):
    """Always returns the same action."""

    def __init__(self, action: Any):
        self.action = action

    def select_action(
        self,
        state: EncodedState,
        actions: Sequence[Any],
        value_fn: ValueFn,
        rng: np.random.Generator,
    ) -> Any:
        return self.action

    def action_distribution(
        self,
        state: EncodedState,
        actions: Sequence[Any],
        value_fn: ValueFn,
    ) -> dict[Any, float]:
        pool = list(actions) if actions else [self.action]
        if self.action not in pool:
            pool.append(self.action)
        return {action: 1.0 if action == self.action else 0.0 for action in pool}
