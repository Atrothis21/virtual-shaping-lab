# policies/fixed_policy.py

"""
Fixed policy for classical conditioning or control experiments.
"""

from typing import Any
import numpy as np

from agents.policies.base import Policy, ValueFn


class FixedPolicy(Policy):
    """
    Always returns the same action.
    """

    def __init__(self, action: Any):
        self.action = action

    def select_action(self, state: np.ndarray, value_fn: ValueFn) -> Any:
        return self.action

