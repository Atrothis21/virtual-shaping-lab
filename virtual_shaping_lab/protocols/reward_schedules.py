# protocols/reward_schedules.py

import random

from .schedule_runtime import (
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
    """
    Base class for operant reward schedules.

    A reward schedule determines whether reinforcement
    is delivered given an action and time.

    Assumes that each call to `step()` corresponds to
    a response opportunity.
    """

    name = "base"

    def reset(self):
        """Reset internal state at experiment start."""
        pass

    def step(self, action, t) -> float:
        """
        Determine reward delivery.

        Parameters
        ----------
        action : Any
            Action emitted by the agent. None indicates no response.
        t : int
            Current trial index.

        Returns
        -------
        reward : float
            Reward magnitude (typically 0 or 1).
        """
        raise NotImplementedError

    def build_tick_runtime(self, time_spec):
        """Optional tick-native schedule runtime adapter."""
        return None


# -------------------------------------------------
# Ratio schedules
# -------------------------------------------------

class FixedRatioSchedule(RewardSchedule):
    """
    Fixed Ratio (FR-n)

    Reinforce every n responses.
    """

    name = "fixed_ratio"

    def __init__(self, n: int, reward: float = 1.0):
        self.n = n
        self.reward = reward
        self._count = 0

    def reset(self):
        self._count = 0

    def step(self, action, t):
        # Only count actual responses
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
    """
    Variable Ratio (VR-n)

    Reinforce responses with probability 1/n.
    """

    name = "variable_ratio"

    def __init__(self, mean_n: int, reward: float = 1.0):
        self.mean_n = mean_n
        self.reward = reward

    def reset(self):
        # Stateless schedule
        pass

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


# -------------------------------------------------
# Interval schedules
# -------------------------------------------------

class FixedIntervalSchedule(RewardSchedule):
    """
    Fixed Interval (FI-t)

    Reinforce the first response after t trials.
    """

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
    """
    Variable Interval (VI-t)

    Reinforce the first response after a variable interval
    with mean t (measured in trials).
    """

    name = "variable_interval"

    def __init__(self, mean_interval: int, reward: float = 1.0):
        self.mean_interval = mean_interval
        self.reward = reward
        self._next_available = 0

    def reset(self):
        self._next_available = self._sample_interval()

    def _sample_interval(self):
        # Exponential distribution with mean = mean_interval
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
