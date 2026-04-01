"""Typed compositional-agent specification for V3.20.15."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any, Mapping

from .learning import LearnerSpec
from .observation import ObservationSpec
from .policy import PolicySpec
from .validation import validate_agent_spec


def _to_primitive(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(k): _to_primitive(v) for k, v in sorted(value.items(), key=lambda item: str(item[0]))}
    if isinstance(value, list):
        return [_to_primitive(v) for v in value]
    if isinstance(value, tuple):
        return [_to_primitive(v) for v in value]
    return value


def _coerce_observation_spec(value: ObservationSpec | Mapping[str, Any]) -> ObservationSpec:
    if isinstance(value, ObservationSpec):
        return value
    if isinstance(value, Mapping):
        return ObservationSpec.from_dict(dict(value))
    raise ValueError("AgentSpec.observation_spec must be ObservationSpec or object payload.")


def _coerce_learner_spec(value: LearnerSpec | Mapping[str, Any]) -> LearnerSpec:
    if isinstance(value, LearnerSpec):
        return value
    if isinstance(value, Mapping):
        return LearnerSpec.from_dict(dict(value))
    raise ValueError("AgentSpec.learner_spec must be LearnerSpec or object payload.")


def _coerce_policy_spec(value: PolicySpec | Mapping[str, Any]) -> PolicySpec:
    if isinstance(value, PolicySpec):
        return value
    if isinstance(value, Mapping):
        return PolicySpec.from_dict(dict(value))
    raise ValueError("AgentSpec.policy_spec must be PolicySpec or object payload.")


@dataclass(frozen=True)
class AgentSpec:
    """Declarative compositional agent contract across observation/learner/policy seams."""

    observation_spec: ObservationSpec | Mapping[str, Any]
    learner_spec: LearnerSpec | Mapping[str, Any]
    policy_spec: PolicySpec | Mapping[str, Any]
    protocol_action_space: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "observation_spec", _coerce_observation_spec(self.observation_spec))
        object.__setattr__(self, "learner_spec", _coerce_learner_spec(self.learner_spec))
        object.__setattr__(self, "policy_spec", _coerce_policy_spec(self.policy_spec))
        if not isinstance(self.protocol_action_space, str) or not self.protocol_action_space.strip():
            raise ValueError("AgentSpec.protocol_action_space must be a non-empty string.")
        object.__setattr__(self, "protocol_action_space", self.protocol_action_space.strip())
        if not isinstance(self.metadata, dict):
            raise ValueError("AgentSpec.metadata must be an object.")
        object.__setattr__(self, "metadata", dict(self.metadata))
        validate_agent_spec(self)

    def to_dict(self) -> dict[str, Any]:
        return {
            "observation_spec": self.observation_spec.to_dict(),
            "learner_spec": self.learner_spec.to_dict(),
            "policy_spec": self.policy_spec.to_dict(),
            "protocol_action_space": self.protocol_action_space,
            "metadata": _to_primitive(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "AgentSpec":
        return cls(
            observation_spec=data.get("observation_spec", {}),
            learner_spec=data.get("learner_spec", {}),
            policy_spec=data.get("policy_spec", {}),
            protocol_action_space=str(data.get("protocol_action_space", "")),
            metadata=dict(data.get("metadata", {}) or {}),
        )

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), sort_keys=True, separators=(",", ":"))

    def stable_hash(self) -> str:
        return hashlib.sha256(self.to_json().encode("utf-8")).hexdigest()

