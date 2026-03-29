"""Typed semantic spec models for V3 (slice 1)."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any


def _require_non_empty_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} must be a non-empty string.")
    return value.strip()


def _require_mapping(value: Any, field_name: str) -> dict[str, Any]:
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise ValueError(f"{field_name} must be an object.")
    return dict(value)


def _to_primitive(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(k): _to_primitive(v) for k, v in sorted(value.items(), key=lambda item: str(item[0]))}
    if isinstance(value, list):
        return [_to_primitive(v) for v in value]
    if isinstance(value, tuple):
        return [_to_primitive(v) for v in value]
    if hasattr(value, "to_dict"):
        return _to_primitive(value.to_dict())
    return value


@dataclass(frozen=True)
class RepresentationSpec:
    name: str
    params: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "name", _require_non_empty_string(self.name, "RepresentationSpec.name"))
        object.__setattr__(self, "params", _require_mapping(self.params, "RepresentationSpec.params"))

    def to_dict(self) -> dict[str, Any]:
        return {"name": self.name, "params": _to_primitive(self.params)}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "RepresentationSpec":
        return cls(name=data.get("name", ""), params=data.get("params", {}))


@dataclass(frozen=True)
class LearnerSpec:
    """Runtime transport learner config.

    This type is intentionally runtime-facing. Canonical learner composition
    semantics are owned by `vsl.agent.learning.spec.LearnerSpec`.
    """
    rule: str
    params: dict[str, Any] = field(default_factory=dict)
    attention_initial: dict[str, Any] = field(default_factory=dict)
    attention_config: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "rule", _require_non_empty_string(self.rule, "LearnerSpec.rule"))
        object.__setattr__(self, "params", _require_mapping(self.params, "LearnerSpec.params"))
        object.__setattr__(
            self, "attention_initial", _require_mapping(self.attention_initial, "LearnerSpec.attention_initial")
        )
        object.__setattr__(
            self, "attention_config", _require_mapping(self.attention_config, "LearnerSpec.attention_config")
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "rule": self.rule,
            "params": _to_primitive(self.params),
            "attention": {
                "initial": _to_primitive(self.attention_initial),
                "config": _to_primitive(self.attention_config),
            },
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "LearnerSpec":
        attention = data.get("attention", {})
        if not isinstance(attention, dict):
            attention = {}
        return cls(
            rule=data.get("rule", ""),
            params=data.get("params", {}),
            attention_initial=attention.get("initial", {}),
            attention_config=attention.get("config", {}),
        )


@dataclass(frozen=True)
class PolicySpec:
    name: str
    params: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "name", _require_non_empty_string(self.name, "PolicySpec.name"))
        object.__setattr__(self, "params", _require_mapping(self.params, "PolicySpec.params"))

    def to_dict(self) -> dict[str, Any]:
        return {"name": self.name, "params": _to_primitive(self.params)}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "PolicySpec":
        return cls(name=data.get("name", ""), params=data.get("params", {}))


@dataclass(frozen=True)
class AgentSpec:
    agent: str
    representation: RepresentationSpec
    learner: LearnerSpec
    policy: PolicySpec | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "agent", _require_non_empty_string(self.agent, "AgentSpec.agent"))
        if not isinstance(self.representation, RepresentationSpec):
            raise ValueError("AgentSpec.representation must be a RepresentationSpec.")
        if not isinstance(self.learner, LearnerSpec):
            raise ValueError("AgentSpec.learner must be a LearnerSpec.")
        if self.policy is not None and not isinstance(self.policy, PolicySpec):
            raise ValueError("AgentSpec.policy must be a PolicySpec when provided.")

    def to_dict(self) -> dict[str, Any]:
        return {
            "agent": self.agent,
            "representation": self.representation.to_dict(),
            "learning": self.learner.to_dict(),
            "policy": None if self.policy is None else self.policy.to_dict(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "AgentSpec":
        policy_data = data.get("policy")
        return cls(
            agent=data.get("agent", ""),
            representation=RepresentationSpec.from_dict(data.get("representation", {})),
            learner=LearnerSpec.from_dict(data.get("learning", {})),
            policy=PolicySpec.from_dict(policy_data) if isinstance(policy_data, dict) else None,
        )


@dataclass(frozen=True)
class ProgramSpec:
    phases: list[dict[str, Any]] = field(default_factory=list)
    resolved_phase_contexts: list[str | None] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not isinstance(self.phases, list):
            raise ValueError("ProgramSpec.phases must be a list.")
        if not isinstance(self.resolved_phase_contexts, list):
            raise ValueError("ProgramSpec.resolved_phase_contexts must be a list.")

    def to_dict(self) -> dict[str, Any]:
        return {
            "phases": _to_primitive(self.phases),
            "resolved_phase_contexts": _to_primitive(self.resolved_phase_contexts),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ProgramSpec":
        return cls(
            phases=list(data.get("phases", []) or []),
            resolved_phase_contexts=list(data.get("resolved_phase_contexts", []) or []),
        )


@dataclass(frozen=True)
class RuntimeSpec:
    runtime: dict[str, Any] = field(default_factory=dict)
    context_inference: dict[str, Any] = field(default_factory=dict)
    resolved_plan: bool = True
    composed_parameters: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "runtime", _require_mapping(self.runtime, "RuntimeSpec.runtime"))
        object.__setattr__(
            self, "context_inference", _require_mapping(self.context_inference, "RuntimeSpec.context_inference")
        )
        object.__setattr__(
            self, "composed_parameters", _require_mapping(self.composed_parameters, "RuntimeSpec.composed_parameters")
        )
        if not isinstance(self.resolved_plan, bool):
            raise ValueError("RuntimeSpec.resolved_plan must be a bool.")

    def to_dict(self) -> dict[str, Any]:
        return {
            "runtime": _to_primitive(self.runtime),
            "context_inference": _to_primitive(self.context_inference),
            "resolved_plan": self.resolved_plan,
            "composed_parameters": _to_primitive(self.composed_parameters),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "RuntimeSpec":
        return cls(
            runtime=data.get("runtime", {}),
            context_inference=data.get("context_inference", {}),
            resolved_plan=bool(data.get("resolved_plan", True)),
            composed_parameters=data.get("composed_parameters", {}),
        )


@dataclass(frozen=True)
class AnalysisSpec:
    report_preset: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "report_preset", _require_non_empty_string(self.report_preset, "AnalysisSpec.report_preset"))

    def to_dict(self) -> dict[str, Any]:
        return {"report_preset": self.report_preset}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "AnalysisSpec":
        return cls(report_preset=data.get("report_preset", ""))


@dataclass(frozen=True)
class EnvironmentProgramSpec:
    segments: list[dict[str, Any]] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.segments, list):
            raise ValueError("EnvironmentProgramSpec.segments must be a list.")
        object.__setattr__(self, "metadata", _require_mapping(self.metadata, "EnvironmentProgramSpec.metadata"))

    def to_dict(self) -> dict[str, Any]:
        return {"segments": _to_primitive(self.segments), "metadata": _to_primitive(self.metadata)}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "EnvironmentProgramSpec":
        return cls(
            segments=list(data.get("segments", []) or []),
            metadata=data.get("metadata", {}),
        )


@dataclass(frozen=True)
class ExperimentSpec:
    program: ProgramSpec
    agent: AgentSpec
    runtime: RuntimeSpec
    analysis: AnalysisSpec
    environment_program: EnvironmentProgramSpec = field(default_factory=EnvironmentProgramSpec)
    canonical_payload: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.program, ProgramSpec):
            raise ValueError("ExperimentSpec.program must be a ProgramSpec.")
        if not isinstance(self.agent, AgentSpec):
            raise ValueError("ExperimentSpec.agent must be an AgentSpec.")
        if not isinstance(self.runtime, RuntimeSpec):
            raise ValueError("ExperimentSpec.runtime must be a RuntimeSpec.")
        if not isinstance(self.analysis, AnalysisSpec):
            raise ValueError("ExperimentSpec.analysis must be an AnalysisSpec.")
        if not isinstance(self.environment_program, EnvironmentProgramSpec):
            raise ValueError("ExperimentSpec.environment_program must be an EnvironmentProgramSpec.")
        object.__setattr__(self, "canonical_payload", _require_mapping(self.canonical_payload, "ExperimentSpec.canonical_payload"))

    def to_dict(self) -> dict[str, Any]:
        return {
            "program": self.program.to_dict(),
            "agent": self.agent.to_dict(),
            "runtime": self.runtime.to_dict(),
            "analysis": self.analysis.to_dict(),
            "environment_program": self.environment_program.to_dict(),
            "canonical_payload": _to_primitive(self.canonical_payload),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ExperimentSpec":
        return cls(
            program=ProgramSpec.from_dict(data.get("program", {})),
            agent=AgentSpec.from_dict(data.get("agent", {})),
            runtime=RuntimeSpec.from_dict(data.get("runtime", {})),
            analysis=AnalysisSpec.from_dict(data.get("analysis", {})),
            environment_program=EnvironmentProgramSpec.from_dict(data.get("environment_program", {})),
            canonical_payload=data.get("canonical_payload", {}),
        )

    def to_json(self) -> str:
        """Deterministic JSON serialization for typed-spec roundtrip and hashing."""
        return json.dumps(self.to_dict(), sort_keys=True, separators=(",", ":"))

    @classmethod
    def from_json(cls, text: str) -> "ExperimentSpec":
        data = json.loads(text)
        if not isinstance(data, dict):
            raise ValueError("ExperimentSpec JSON payload must decode to an object.")
        return cls.from_dict(data)

    def stable_hash(self) -> str:
        """Stable semantic hash for deterministic identity checks."""
        return hashlib.sha256(self.to_json().encode("utf-8")).hexdigest()


# V3.18.0 ownership clarity alias.
RuntimeLearnerConfig = LearnerSpec
