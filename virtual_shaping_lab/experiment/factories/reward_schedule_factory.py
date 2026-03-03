"""Compatibility factory for reward schedule construction.

Canonical registry and implementations are world-owned:
`virtual_shaping_lab.experiment.world.schedules.reward_schedules`.
"""

from virtual_shaping_lab.experiment.world.schedules import reward_schedules as world_reward_schedules


# Alias to canonical world registry object.
REWARD_SCHEDULE_REGISTRY = world_reward_schedules.REWARD_SCHEDULE_REGISTRY


def validate_reward_schedule(name: str) -> None:
    if name not in REWARD_SCHEDULE_REGISTRY:
        available = ", ".join(sorted(REWARD_SCHEDULE_REGISTRY.keys()))
        raise KeyError(
            f"Unknown reward schedule '{name}'. "
            f"Available schedules: {available}"
        )


def build_reward_schedule(config: dict):
    """
    Construct a RewardSchedule from config.

    Expected config format:
        {
          "type": "fixed_ratio" | "variable_ratio" | "fixed_interval" | "variable_interval",
          "value": int | float
        }
    """
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

