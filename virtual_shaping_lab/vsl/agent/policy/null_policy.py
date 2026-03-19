"""Null policy for actionless V3 execution paths."""

from __future__ import annotations

from typing import Any

import numpy as np

from .action_space import ActionSpace


class NullPolicy:
    """Policy that deterministically emits no action."""

    def reset(self) -> None:
        return None

    def select_action(
        self,
        state: Any,
        action_space: ActionSpace,
        rng: np.random.Generator,
    ) -> None:
        return None

    def action_distribution(
        self,
        state: Any,
        action_space: ActionSpace,
    ) -> dict[Any, float]:
        actions = tuple(action_space.actions())
        if not actions:
            return {}
        if len(actions) == 1:
            return {actions[0]: 1.0}
        return {action: 0.0 for action in actions}

