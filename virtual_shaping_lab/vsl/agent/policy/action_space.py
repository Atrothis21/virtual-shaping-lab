"""Action-space primitives for V3 policy semantics."""

from __future__ import annotations

from typing import Any, Protocol

import numpy as np


class ActionSpace(Protocol):
    """Minimal action-space contract for policy selection."""

    def actions(self) -> tuple[Any, ...]:
        raise NotImplementedError

    def sample(self, rng: np.random.Generator) -> Any | None:
        raise NotImplementedError


class NullActionSpace:
    """Action-space with no available actions."""

    def actions(self) -> tuple[Any, ...]:
        return ()

    def sample(self, rng: np.random.Generator) -> None:
        return None


class SingletonActionSpace:
    """Action-space with one deterministic action."""

    def __init__(self, action: Any = None) -> None:
        self._action = action

    def actions(self) -> tuple[Any, ...]:
        return (self._action,)

    def sample(self, rng: np.random.Generator) -> Any:
        return self._action

