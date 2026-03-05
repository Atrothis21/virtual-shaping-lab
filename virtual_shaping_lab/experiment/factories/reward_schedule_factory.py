"""Strict adapter for world-owned reward schedule construction.

Canonical ownership lives in:
`virtual_shaping_lab.experiment.world.schedules.reward_schedules`.
This module provides the experiment/factories seam without duplicating
registry or construction logic.
"""

from virtual_shaping_lab.experiment.world.schedules import reward_schedules as world_reward_schedules


# Single-owner alias to canonical world registry object.
REWARD_SCHEDULE_REGISTRY = world_reward_schedules.REWARD_SCHEDULE_REGISTRY


def validate_reward_schedule(name: str) -> None:
    world_reward_schedules.validate_reward_schedule(name)


def build_reward_schedule(config: dict):
    return world_reward_schedules.build_reward_schedule(config)

