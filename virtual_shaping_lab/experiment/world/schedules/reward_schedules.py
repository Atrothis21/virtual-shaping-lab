"""Canonical reward schedule implementations and registry."""

from __future__ import annotations

import random
from typing import Dict, Type

from virtual_shaping_lab.experiment.world.schedules import (
    AlwaysAvailable,
    ConstantConsequenceMapper,
    FixedIntervalAvailability,
    FixedRatioGate,
    FirstResponseGate,
    TickScheduleRuntime,
    VariableIntervalAvailability,
    VariableRatioGate,
)


class RewardSchedule:
    """Base class for operant reward schedules."""

    name = "base"

    def reset(self):
        return None

    def step(self, action, t) -> float:
        raise NotImplementedError

    def build_tick_runtime(self, time_spec):
        return None


class FixedRatioSchedule(RewardSchedule):
    name = "fixed_ratio"

    def __init__(self, n: int, reward: float = 1.0):
        self.n = n
        self.reward = reward
        self._count = 0

    def reset(self):
        self._count = 0

    def step(self, action, t):
        if action is None:
            return 0.0
        self._count += 1
        if self._count >= self.n:
            self._count = 0
            return self.reward
        return 0.0

    def build_tick_runtime(self, time_spec):
        return TickScheduleRuntime(
            availability=AlwaysAvailable(),
            gate=FixedRatioGate(n=self.n),
            consequence_mapper=ConstantConsequenceMapper(reward=self.reward),
        )


class VariableRatioSchedule(RewardSchedule):
    name = "variable_ratio"

    def __init__(self, mean_n: int, reward: float = 1.0):
        self.mean_n = mean_n
        self.reward = reward

    def step(self, action, t):
        if action is None:
            return 0.0
        if random.random() < (1.0 / self.mean_n):
            return self.reward
        return 0.0

    def build_tick_runtime(self, time_spec):
        return TickScheduleRuntime(
            availability=AlwaysAvailable(),
            gate=VariableRatioGate(mean_n=self.mean_n),
            consequence_mapper=ConstantConsequenceMapper(reward=self.reward),
        )


class FixedIntervalSchedule(RewardSchedule):
    name = "fixed_interval"

    def __init__(self, interval: int, reward: float = 1.0):
        self.interval = interval
        self.reward = reward
        self._last_reinforcement = 0

    def reset(self):
        self._last_reinforcement = 0

    def step(self, action, t):
        if action is None:
            return 0.0
        if (t - self._last_reinforcement) >= self.interval:
            self._last_reinforcement = t
            return self.reward
        return 0.0

    def build_tick_runtime(self, time_spec):
        dt_s = float(getattr(time_spec, "dt_s", 1.0) or 1.0)
        interval_s = float(self.interval) * dt_s
        return TickScheduleRuntime(
            availability=FixedIntervalAvailability(interval_s=max(interval_s, 1e-12)),
            gate=FirstResponseGate(),
            consequence_mapper=ConstantConsequenceMapper(reward=self.reward),
        )


class VariableIntervalSchedule(RewardSchedule):
    name = "variable_interval"

    def __init__(self, mean_interval: int, reward: float = 1.0):
        self.mean_interval = mean_interval
        self.reward = reward
        self._next_available = 0

    def reset(self):
        self._next_available = self._sample_interval()

    def _sample_interval(self):
        return random.expovariate(1.0 / self.mean_interval)

    def step(self, action, t):
        if action is None:
            return 0.0
        if t >= self._next_available:
            self._next_available = t + self._sample_interval()
            return self.reward
        return 0.0

    def build_tick_runtime(self, time_spec):
        dt_s = float(getattr(time_spec, "dt_s", 1.0) or 1.0)
        mean_interval_s = float(self.mean_interval) * dt_s
        return TickScheduleRuntime(
            availability=VariableIntervalAvailability(mean_interval_s=max(mean_interval_s, 1e-12)),
            gate=FirstResponseGate(),
            consequence_mapper=ConstantConsequenceMapper(reward=self.reward),
        )


REWARD_SCHEDULE_REGISTRY: Dict[str, Type] = {
    "fixed_ratio": FixedRatioSchedule,
    "variable_ratio": VariableRatioSchedule,
    "fixed_interval": FixedIntervalSchedule,
    "variable_interval": VariableIntervalSchedule,
}


def validate_reward_schedule(name: str) -> None:
    if name not in REWARD_SCHEDULE_REGISTRY:
        available = ", ".join(sorted(REWARD_SCHEDULE_REGISTRY.keys()))
        raise KeyError(
            f"Unknown reward schedule '{name}'. "
            f"Available schedules: {available}"
        )


def build_reward_schedule(config: dict):
    if not isinstance(config, dict):
        raise TypeError(
            "Reward schedule config must be a dict with keys "
            "'type' and 'value'."
        )
    if "type" not in config:
        raise KeyError("Reward schedule config missing required key: 'type'")
    if "value" not in config:
        raise KeyError("Reward schedule config missing required key: 'value'")

    schedule_type = config["type"]
    value = config["value"]
    reward = config.get("reward", 1.0)
    validate_reward_schedule(schedule_type)
    schedule_cls = REWARD_SCHEDULE_REGISTRY[schedule_type]

    if schedule_type == "fixed_ratio":
        return schedule_cls(n=value, reward=reward)
    if schedule_type == "variable_ratio":
        return schedule_cls(mean_n=value, reward=reward)
    if schedule_type == "fixed_interval":
        return schedule_cls(interval=value, reward=reward)
    if schedule_type == "variable_interval":
        return schedule_cls(mean_interval=value, reward=reward)
    raise RuntimeError(f"Unhandled reward schedule type '{schedule_type}'")

