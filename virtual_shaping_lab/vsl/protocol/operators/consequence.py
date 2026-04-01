"""Executable protocol consequence operators."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping

from virtual_shaping_lab.vsl.protocol.output import ConsequenceOutput, EmissionOutput


@dataclass(frozen=True)
class ActionConditionedConsequenceOperator:
    """Map action to deterministic consequence (reward/done)."""

    reward_by_action: dict[str, float] = field(default_factory=dict)
    default_reward: float = 0.0
    terminal_actions: tuple[Any, ...] = field(default_factory=tuple)
    variant: str = "action_conditioned_consequence"

    def __post_init__(self) -> None:
        if not isinstance(self.reward_by_action, dict):
            raise ValueError("ActionConditionedConsequenceOperator.reward_by_action must be an object.")
        object.__setattr__(self, "reward_by_action", {str(k): float(v) for k, v in self.reward_by_action.items()})
        object.__setattr__(self, "default_reward", float(self.default_reward))
        object.__setattr__(self, "terminal_actions", tuple(self.terminal_actions))

    def consequence(
        self,
        *,
        emission: EmissionOutput,
        action: Any,
        state: Mapping[str, Any],
        metadata: Mapping[str, Any] | None = None,
    ) -> ConsequenceOutput:
        _ = emission
        action_key = str(action)
        reward = float(self.reward_by_action.get(action_key, self.default_reward))
        done = action in self.terminal_actions or bool(dict(state).get("done", False))
        merged_meta = dict(metadata or {})
        merged_meta.setdefault("variant", self.variant)
        merged_meta.setdefault("action", action)
        return ConsequenceOutput(
            reward=reward,
            done=done,
            outcome_state={},
            metadata=merged_meta,
        )


@dataclass(frozen=True)
class ClassicalNoActionConsequenceOperator:
    """Consequence operator for classical/no-action protocols."""

    reward: float = 1.0
    reward_schedule: tuple[float, ...] = field(default_factory=tuple)
    done: bool = False
    variant: str = "classical_no_action_consequence"

    def __post_init__(self) -> None:
        object.__setattr__(self, "reward", float(self.reward))
        object.__setattr__(self, "reward_schedule", tuple(float(v) for v in self.reward_schedule))
        object.__setattr__(self, "done", bool(self.done))

    def consequence(
        self,
        *,
        emission: EmissionOutput,
        action: Any,
        state: Mapping[str, Any],
        metadata: Mapping[str, Any] | None = None,
    ) -> ConsequenceOutput:
        _ = emission
        raw_t = int(dict(state).get("t", 0))
        reward_value = self.reward
        if self.reward_schedule:
            idx = max(0, min(raw_t, len(self.reward_schedule) - 1))
            reward_value = float(self.reward_schedule[idx])
        merged_meta = dict(metadata or {})
        merged_meta.setdefault("variant", self.variant)
        merged_meta.setdefault("action_ignored", action)
        return ConsequenceOutput(
            reward=reward_value,
            done=self.done or bool(dict(state).get("done", False)),
            outcome_state={},
            metadata=merged_meta,
        )
