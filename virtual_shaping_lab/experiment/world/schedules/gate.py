"""Reinforcement gate contracts and implementations."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

import numpy as np


class ReinforcementGate(ABC):
    @abstractmethod
    def reset(self, rng: np.random.Generator) -> None:
        raise NotImplementedError

    @abstractmethod
    def should_collect(self, action: Any, available: bool) -> bool:
        raise NotImplementedError


class FirstResponseGate(ReinforcementGate):
    def reset(self, rng: np.random.Generator) -> None:
        return None

    def should_collect(self, action: Any, available: bool) -> bool:
        return bool(available and action is not None)


class FixedRatioGate(ReinforcementGate):
    def __init__(self, n: int):
        self.n = int(n)
        self._count = 0

    def reset(self, rng: np.random.Generator) -> None:
        self._count = 0

    def should_collect(self, action: Any, available: bool) -> bool:
        if action is None:
            return False
        self._count += 1
        if self._count >= self.n:
            self._count = 0
            return True
        return False


class VariableRatioGate(ReinforcementGate):
    def __init__(self, mean_n: float):
        self.mean_n = float(mean_n)
        self._rng = np.random.default_rng()

    def reset(self, rng: np.random.Generator) -> None:
        self._rng = rng

    def should_collect(self, action: Any, available: bool) -> bool:
        if action is None:
            return False
        p = 1.0 / max(self.mean_n, 1e-12)
        return bool(self._rng.random() < p)

