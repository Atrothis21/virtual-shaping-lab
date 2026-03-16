# policies/base.py

"""Policy contract bridge aligned to v2 composition interfaces."""

from __future__ import annotations

from abc import abstractmethod
from typing import Any, Sequence

import numpy as np

from virtual_shaping_lab.agents.interfaces import IPolicy, ValueFn
from virtual_shaping_lab.domain.types import EncodedState


class Policy(IPolicy):
    """Abstract base class for concrete action-selection policies."""

    def reset(self) -> None:
        return None

    def action_distribution(
        self,
        state: EncodedState,
        actions: Sequence[Any],
        value_fn: ValueFn,
    ) -> dict[Any, float] | None:
        return None

    @abstractmethod
    def select_action(
        self,
        state: EncodedState,
        actions: Sequence[Any],
        value_fn: ValueFn,
        rng: np.random.Generator,
    ) -> Any:
        raise NotImplementedError
