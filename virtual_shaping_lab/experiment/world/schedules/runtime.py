"""Tick-native operant schedule runtime composites."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np

from virtual_shaping_lab.experiment.world.schedules.availability import AvailabilityProcess
from virtual_shaping_lab.experiment.world.schedules.consequence import ConsequenceMapper
from virtual_shaping_lab.experiment.world.schedules.gate import ReinforcementGate


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

