"""Compositional-agent instantiation boundary from typed specs to subsystem contracts."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping

from .learning import (
    LearnerInstantiationArtifact,
    instantiate_learner_contracts,
)
from .observation import (
    ObservationInstantiationArtifact,
    instantiate_observation_contracts,
)
from .policy import (
    PolicyInstantiationArtifact,
    instantiate_policy_contracts,
)
from .spec import AgentSpec
from .validation import AgentSpecValidationError


AGENT_INSTANTIATION_FAILURES: dict[str, str] = {
    "INST_E_INVALID_SPEC_INPUT": "Agent spec input must be AgentSpec or object payload.",
    "INST_E_LEGALITY": "Agent spec failed legality validation before materialization.",
    "INST_E_BOUNDARY_RESOLUTION": "Agent boundary resolution failed for subsystem inputs.",
}


@dataclass
class AgentInstantiationError(ValueError):
    code: str
    message: str
    details: dict[str, Any] = field(default_factory=dict)

    def __str__(self) -> str:
        return f"[{self.code}] {self.message}"


@dataclass(frozen=True)
class AgentInstantiationArtifact:
    agent_spec: AgentSpec
    observation: ObservationInstantiationArtifact
    learner: LearnerInstantiationArtifact
    policy: PolicyInstantiationArtifact
    composition_hash: str


def _coerce_agent_spec(spec: AgentSpec | Mapping[str, Any]) -> AgentSpec:
    if isinstance(spec, AgentSpec):
        return spec
    if isinstance(spec, Mapping):
        try:
            return AgentSpec.from_dict(dict(spec))
        except (AgentSpecValidationError, ValueError, TypeError) as exc:
            raise AgentInstantiationError(
                "INST_E_LEGALITY",
                AGENT_INSTANTIATION_FAILURES["INST_E_LEGALITY"],
                details={"reason": str(exc)},
            ) from exc
    raise AgentInstantiationError(
        "INST_E_INVALID_SPEC_INPUT",
        AGENT_INSTANTIATION_FAILURES["INST_E_INVALID_SPEC_INPUT"],
    )


def instantiate_agent_contracts(spec: AgentSpec | Mapping[str, Any]) -> AgentInstantiationArtifact:
    """Materialize typed compositional-agent contracts from canonical AgentSpec."""
    agent_spec = _coerce_agent_spec(spec)
    observation_artifact = instantiate_observation_contracts(agent_spec.observation_spec)
    learner_artifact = instantiate_learner_contracts(agent_spec.learner_spec)
    policy_artifact = instantiate_policy_contracts(agent_spec.policy_spec)
    return AgentInstantiationArtifact(
        agent_spec=agent_spec,
        observation=observation_artifact,
        learner=learner_artifact,
        policy=policy_artifact,
        composition_hash=agent_spec.stable_hash(),
    )


def instantiate_agent_from_boundary(
    *,
    observation_spec: Mapping[str, Any] | Any,
    learner_spec: Mapping[str, Any] | Any,
    policy_spec: Mapping[str, Any] | Any,
    protocol_action_space: str,
    metadata: Mapping[str, Any] | None = None,
) -> AgentInstantiationArtifact:
    """Resolve subsystem boundary payloads and materialize typed compositional-agent contracts."""
    try:
        spec = AgentSpec(
            observation_spec=observation_spec,
            learner_spec=learner_spec,
            policy_spec=policy_spec,
            protocol_action_space=protocol_action_space,
            metadata=dict(metadata or {}),
        )
    except Exception as exc:
        raise AgentInstantiationError(
            "INST_E_BOUNDARY_RESOLUTION",
            AGENT_INSTANTIATION_FAILURES["INST_E_BOUNDARY_RESOLUTION"],
            details={"reason": str(exc)},
        ) from exc
    return instantiate_agent_contracts(spec)

