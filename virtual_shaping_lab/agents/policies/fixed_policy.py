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
