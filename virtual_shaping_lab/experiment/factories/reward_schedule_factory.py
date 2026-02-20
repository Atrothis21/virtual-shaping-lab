# experiment/factories/reward_schedule_factory.py

from typing import Dict, Type

from protocols.reward_schedules import (
    FixedRatioSchedule,
    VariableRatioSchedule,
    FixedIntervalSchedule,
    VariableIntervalSchedule,
)


# -------------------------------------------------
# Registry
# -------------------------------------------------

REWARD_SCHEDULE_REGISTRY: Dict[str, Type] = {
    "fixed_ratio": FixedRatioSchedule,
    "variable_ratio": VariableRatioSchedule,
    "fixed_interval": FixedIntervalSchedule,
    "variable_interval": VariableIntervalSchedule,
}


# -------------------------------------------------
# Validation
# -------------------------------------------------

def validate_reward_schedule(name: str) -> None:
    if name not in REWARD_SCHEDULE_REGISTRY:
        available = ", ".join(sorted(REWARD_SCHEDULE_REGISTRY.keys()))
        raise KeyError(
            f"Unknown reward schedule '{name}'. "
            f"Available schedules: {available}"
        )


# -------------------------------------------------
# Construction
# -------------------------------------------------

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

    validate_reward_schedule(schedule_type)

    schedule_cls = REWARD_SCHEDULE_REGISTRY[schedule_type]

    # Map semantic value → constructor argument
    if schedule_type == "fixed_ratio":
        return schedule_cls(n=value)

    if schedule_type == "variable_ratio":
        return schedule_cls(mean_n=value)

    if schedule_type == "fixed_interval":
        return schedule_cls(interval=value)

    if schedule_type == "variable_interval":
        return schedule_cls(mean_interval=value)

    # Defensive fallback (should never happen)
    raise RuntimeError(
        f"Unhandled reward schedule type '{schedule_type}'"
    )
