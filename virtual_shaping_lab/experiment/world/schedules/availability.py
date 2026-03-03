"""Availability process contracts and implementations."""

from __future__ import annotations

from abc import ABC, abstractmethod

import numpy as np


class AvailabilityProcess(ABC):
    @abstractmethod
    def reset(self, rng: np.random.Generator) -> None:
        raise NotImplementedError

    @abstractmethod
    def advance(self, t_s: float, dt_s: float) -> bool:
        raise NotImplementedError

    @abstractmethod
    def consume(self, t_s: float, dt_s: float) -> None:
        raise NotImplementedError

    @property
    @abstractmethod
    def is_available(self) -> bool:
        raise NotImplementedError


class AlwaysAvailable(AvailabilityProcess):
    def reset(self, rng: np.random.Generator) -> None:
        return None

    def advance(self, t_s: float, dt_s: float) -> bool:
        return True

    def consume(self, t_s: float, dt_s: float) -> None:
        return None

    @property
    def is_available(self) -> bool:
        return True


class FixedIntervalAvailability(AvailabilityProcess):
    def __init__(self, interval_s: float):
        self.interval_s = float(interval_s)
        self._available = False
        self._next_available_s = self.interval_s

    def reset(self, rng: np.random.Generator) -> None:
        self._available = False
        self._next_available_s = self.interval_s

    def advance(self, t_s: float, dt_s: float) -> bool:
        if not self._available and (t_s + dt_s) >= self._next_available_s:
            self._available = True
        return self._available

    def consume(self, t_s: float, dt_s: float) -> None:
        self._available = False
        self._next_available_s = (t_s + dt_s) + self.interval_s

    @property
    def is_available(self) -> bool:
        return self._available


class VariableIntervalAvailability(AvailabilityProcess):
    def __init__(self, mean_interval_s: float):
        self.mean_interval_s = float(mean_interval_s)
        self._rng = np.random.default_rng()
        self._available = False
        self._next_available_s = 0.0

    def reset(self, rng: np.random.Generator) -> None:
        self._rng = rng
        self._available = False
        self._next_available_s = self._sample_interval()

    def _sample_interval(self) -> float:
        lam = 1.0 / max(self.mean_interval_s, 1e-12)
        return float(self._rng.exponential(scale=1.0 / lam))

    def advance(self, t_s: float, dt_s: float) -> bool:
        if not self._available and (t_s + dt_s) >= self._next_available_s:
            self._available = True
        return self._available

    def consume(self, t_s: float, dt_s: float) -> None:
        self._available = False
        self._next_available_s = (t_s + dt_s) + self._sample_interval()

    @property
    def is_available(self) -> bool:
        return self._available

