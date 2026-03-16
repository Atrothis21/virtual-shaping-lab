"""Core component interfaces for composition-first agents."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Callable, Sequence

import numpy as np

from virtual_shaping_lab.domain.types import EncodedState, Observation, Transition


ValueFn = Callable[[EncodedState, Any], float]


class IRepresentation(ABC):
    """Encodes raw observations (including optional timing fields) into vectorized states."""

    @abstractmethod
    def reset(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def encode(self, observation: Observation) -> EncodedState:
        raise NotImplementedError


class ILearner(ABC):
    """Owns value function parameters and transition-based learning updates."""

    @abstractmethod
    def reset(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def value(self, state: EncodedState, action: Any = None) -> float:
        raise NotImplementedError

    @abstractmethod
    def update(self, transition: Transition) -> None:
        raise NotImplementedError


class IPolicy(ABC):
    """Selects actions without mutating learner state.

    Mathematically, a policy implements a decision kernel `pi(a | x, theta)`.
    `select_action(...)` samples from that kernel, while `action_distribution(...)`
    optionally exposes the kernel directly for diagnostics and replay inspection.
    """

    @abstractmethod
    def reset(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def select_action(
        self,
        state: EncodedState,
        actions: Sequence[Any],
        value_fn: ValueFn,
        rng: np.random.Generator,
    ) -> Any:
        raise NotImplementedError

    def action_distribution(
        self,
        state: EncodedState,
        actions: Sequence[Any],
        value_fn: ValueFn,
    ) -> dict[Any, float] | None:
        """Return the policy kernel over the provided action set when available."""
        return None
