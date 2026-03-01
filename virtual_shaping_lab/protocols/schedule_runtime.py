"""Tick-native operant schedule runtime contracts and composites."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

import numpy as np


@dataclass(frozen=True)
class ScheduleTickInput:
    t_s: float
    dt_s: float
    action: Any = None
    tick: int | None = None
    trial_id: Any = None


@dataclass(frozen=True)
class ScheduleTickResult:
    available: bool
    collected: bool
    reward: float
    event_type: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


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


class ReinforcementGate(ABC):
    @abstractmethod
    def reset(self, rng: np.random.Generator) -> None:
        raise NotImplementedError

    @abstractmethod
    def should_collect(self, action: Any, available: bool) -> bool:
        raise NotImplementedError


@dataclass(frozen=True)
class Consequence:
    reward: float
    event_type: str | None


class ConsequenceMapper(ABC):
    @abstractmethod
    def map(self, *, collected: bool) -> Consequence:
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


class ConstantConsequenceMapper(ConsequenceMapper):
    def __init__(self, reward: float):
        self.reward = float(reward)

    def map(self, *, collected: bool) -> Consequence:
        if collected:
            event_type = "reinforcement" if self.reward > 0 else ("punishment" if self.reward < 0 else "extinction")
            return Consequence(reward=self.reward, event_type=event_type)
        return Consequence(reward=0.0, event_type=None)


class TickScheduleRuntime:
    """Composition root for tick-native schedule execution."""

    def __init__(
        self,
        *,
        availability: AvailabilityProcess,
        gate: ReinforcementGate,
        consequence_mapper: ConsequenceMapper,
    ):
        self.availability = availability
        self.gate = gate
        self.consequence_mapper = consequence_mapper

    def reset(self, rng: np.random.Generator | None = None) -> None:
        gen = rng if rng is not None else np.random.default_rng()
        self.availability.reset(gen)
        self.gate.reset(gen)

    def step(self, tick_input: ScheduleTickInput) -> ScheduleTickResult:
        available = bool(self.availability.advance(tick_input.t_s, tick_input.dt_s))
        collected = bool(self.gate.should_collect(tick_input.action, available))
        if collected:
            self.availability.consume(tick_input.t_s, tick_input.dt_s)
        consequence = self.consequence_mapper.map(collected=collected)
        return ScheduleTickResult(
            available=available,
            collected=collected,
            reward=consequence.reward,
            event_type=consequence.event_type,
            metadata={"available_after_step": self.availability.is_available},
        )

