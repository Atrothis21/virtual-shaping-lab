"""Compatibility shim for reward schedule imports.

Canonical reward schedules and registry now live under:
`virtual_shaping_lab.experiment.world.schedules.reward_schedules`.
"""

from virtual_shaping_lab.experiment.world.schedules.reward_schedules import (
    FixedIntervalSchedule,
    FixedRatioSchedule,
    RewardSchedule,
    VariableIntervalSchedule,
    VariableRatioSchedule,
    REWARD_SCHEDULE_REGISTRY,
    build_reward_schedule,
    validate_reward_schedule,
)

__all__ = [
    "FixedIntervalSchedule",
    "FixedRatioSchedule",
    "RewardSchedule",
    "VariableIntervalSchedule",
    "VariableRatioSchedule",
    "REWARD_SCHEDULE_REGISTRY",
    "build_reward_schedule",
    "validate_reward_schedule",
]

