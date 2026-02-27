"""Null policy for classical conditioning flows."""

from __future__ import annotations

from typing import Any, Sequence

import numpy as np

from virtual_shaping_lab.agents.interfaces import IPolicy, ValueFn
from virtual_shaping_lab.domain.types import EncodedState


class NullPolicy(IPolicy):
    """Policy that never selects an action."""

    def reset(self) -> None:
        return None

    def select_action(
        self,
        state: EncodedState,
        actions: Sequence[Any],
        value_fn: ValueFn,
        rng: np.random.Generator,
    ) -> Any:
        return None
