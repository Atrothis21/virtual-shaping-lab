"""Typed experiment-agent interaction boundary contracts."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

_DISALLOWED_OUTCOME_KEYS = {"prediction_error", "delta", "theta", "attention", "eligibility"}


def _copy_dict(value: dict[str, Any] | None) -> dict[str, Any]:
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise ValueError("Expected an object.")
    return dict(value)


@dataclass(frozen=True)
class TaskInput:
    """Task-facing experiment emission for pre-outcome agent calls."""

    stimuli: dict[str, Any] = field(default_factory=dict)
    context: str | None = None
    t: int | None = None
    phase: str | None = None
    available_actions: tuple[Any, ...] = field(default_factory=tuple)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "stimuli", _copy_dict(self.stimuli))
        object.__setattr__(self, "metadata", _copy_dict(self.metadata))
        object.__setattr__(self, "available_actions", tuple(self.available_actions))


@dataclass(frozen=True)
class Action:
    """Agent-emitted action contract at the behavioral boundary."""

    value: Any
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "metadata", _copy_dict(self.metadata))


@dataclass(frozen=True)
class Outcome:
    """Experiment-emitted consequence contract at the learning boundary."""

    reward: float | int
    next_stimuli: dict[str, Any] = field(default_factory=dict)
    terminated: bool = False
    truncated: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.reward, (int, float)):
            raise ValueError("Outcome.reward must be numeric.")
        object.__setattr__(self, "next_stimuli", _copy_dict(self.next_stimuli))
        md = _copy_dict(self.metadata)
        forbidden = sorted(_DISALLOWED_OUTCOME_KEYS.intersection(md.keys()))
        if forbidden:
            joined = ", ".join(forbidden)
            raise ValueError(f"Outcome.metadata contains disallowed internal-learning keys: {joined}.")
        object.__setattr__(self, "metadata", md)


@dataclass(frozen=True)
class TrialRecord:
    """Joint measurement record composed from experiment and agent outputs."""

    trial_index: int
    task_input: TaskInput
    action: Action
    outcome: Outcome
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.trial_index, int) or self.trial_index < 0:
            raise ValueError("TrialRecord.trial_index must be a non-negative integer.")
        object.__setattr__(self, "metadata", _copy_dict(self.metadata))


def validate_interaction_boundary(task_input: TaskInput, action: Action, outcome: Outcome) -> None:
    """Validate that typed interaction boundary contracts are respected."""
    if not isinstance(task_input, TaskInput):
        raise TypeError("task_input must be TaskInput.")
    if not isinstance(action, Action):
        raise TypeError("action must be Action.")
    if not isinstance(outcome, Outcome):
        raise TypeError("outcome must be Outcome.")

