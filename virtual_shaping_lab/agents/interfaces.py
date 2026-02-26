"""Core component interfaces for composition-first agents."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Callable, Sequence

import numpy as np

from virtual_shaping_lab.domain.types import EncodedState, Observation, Transition


ValueFn = Callable[[EncodedState, Any], float]


class IRepresentation(ABC):
    """Encodes raw observations into vectorized states."""

    @abstractmethod
    def reset(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def encode(self, observation: Observation) -> EncodedState:
        raise NotImplementedError


class ILearner(ABC):
    """Owns value function parameters and learning updates."""

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
    """Selects actions without mutating learner state."""

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
