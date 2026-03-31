"""Executable policy operator protocols and null/default operators."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, Protocol, runtime_checkable


@dataclass(frozen=True)
class PolicyOutput:
    """Typed policy decision output for runtime/report surfaces."""

    action: Any
    action_scores: dict[Any, float] = field(default_factory=dict)
    action_probabilities: dict[Any, float] = field(default_factory=dict)
    available_actions: tuple[Any, ...] = field(default_factory=tuple)
    policy_state: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.action_scores, dict):
            raise ValueError("PolicyOutput.action_scores must be an object.")
        if not isinstance(self.action_probabilities, dict):
            raise ValueError("PolicyOutput.action_probabilities must be an object.")
        if not isinstance(self.policy_state, dict):
            raise ValueError("PolicyOutput.policy_state must be an object.")
        if not isinstance(self.metadata, dict):
            raise ValueError("PolicyOutput.metadata must be an object.")
        object.__setattr__(self, "available_actions", tuple(self.available_actions))
        object.__setattr__(self, "action_scores", dict(self.action_scores))
        object.__setattr__(self, "action_probabilities", dict(self.action_probabilities))
        object.__setattr__(self, "policy_state", dict(self.policy_state))
        object.__setattr__(self, "metadata", dict(self.metadata))


@runtime_checkable
class PolicyOperator(Protocol):
    """Select action from canonical policy input transport."""

    def select(
        self,
        *,
        policy_input: Mapping[str, Any],
        available_actions: tuple[Any, ...] = (),
        rng: Any | None = None,
        metadata: Mapping[str, Any] | None = None,
    ) -> PolicyOutput: ...


@runtime_checkable
class ActionAvailabilityOperator(Protocol):
    """Optional action availability/masking stage before selection."""

    def filter_actions(
        self,
        *,
        policy_input: Mapping[str, Any],
        available_actions: tuple[Any, ...],
        metadata: Mapping[str, Any] | None = None,
    ) -> tuple[Any, ...]: ...


@dataclass(frozen=True)
class NullPolicyOperator:
    """No-op policy operator for action-absent/classical execution paths."""

    slot: str = "Pi"
    variant: str = "null_policy"

    def select(
        self,
        *,
        policy_input: Mapping[str, Any],
        available_actions: tuple[Any, ...] = (),
        rng: Any | None = None,
        metadata: Mapping[str, Any] | None = None,
    ) -> PolicyOutput:
        _ = policy_input, rng
        md = dict(metadata or {})
        md.setdefault("variant", self.variant)
        return PolicyOutput(
            action=None,
            action_scores={},
            action_probabilities={},
            available_actions=tuple(available_actions),
            policy_state={},
            metadata=md,
        )

