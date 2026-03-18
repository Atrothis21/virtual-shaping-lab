"""Typed canonical builder-draft contracts for UI-authored experiment payloads."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


class BuilderDraftValidationError(ValueError):
    """Raised when a builder draft violates UI contract requirements."""


def _require_dict(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise BuilderDraftValidationError(f"{label} must be an object.")
    return value


def _require_non_empty_string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise BuilderDraftValidationError(f"{label} must be a non-empty string.")
    return value.strip()


def _resolve_trials(params: dict[str, Any]) -> int:
    raw = params.get("n_trials", 1)
    try:
        trials = int(raw)
    except (TypeError, ValueError):
        raise BuilderDraftValidationError("phase.params.n_trials must be an integer.")
    if trials <= 0:
        raise BuilderDraftValidationError("phase.params.n_trials must be > 0.")
    return trials


@dataclass(frozen=True)
class BuilderRuntimeDraft:
    """Runtime draft consumed by the UI builder."""

    seed: int | None = None
    update_mode: str = "trial"
    record_mode: str = "trial"
    strict_records: bool = False
    debug: bool = False
    context_inference: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.seed is not None and not isinstance(self.seed, int):
            raise BuilderDraftValidationError("runtime.seed must be an integer when provided.")
        if self.update_mode not in {"trial", "tick"}:
            raise BuilderDraftValidationError("runtime.update_mode must be 'trial' or 'tick'.")
        if self.record_mode not in {"trial", "tick"}:
            raise BuilderDraftValidationError("runtime.record_mode must be 'trial' or 'tick'.")
        if not isinstance(self.strict_records, bool):
            raise BuilderDraftValidationError("runtime.strict_records must be boolean.")
        if not isinstance(self.debug, bool):
            raise BuilderDraftValidationError("runtime.debug must be boolean.")
        _require_dict(self.context_inference, "runtime.context_inference")

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> "BuilderRuntimeDraft":
        if data is None:
            return cls()
        payload = _require_dict(data, "experiment.runtime")
        return cls(
            seed=payload.get("seed"),
            update_mode=str(payload.get("update_mode", "trial")),
            record_mode=str(payload.get("record_mode", "trial")),
            strict_records=bool(payload.get("strict_records", False)),
            debug=bool(payload.get("debug", False)),
            context_inference=_require_dict(payload.get("context_inference", {}), "runtime.context_inference"),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "seed": self.seed,
            "update_mode": self.update_mode,
            "record_mode": self.record_mode,
            "strict_records": self.strict_records,
            "debug": self.debug,
            "context_inference": dict(self.context_inference),
        }


@dataclass(frozen=True)
class BuilderPhaseDraft:
    """Typed phase draft entry for program.phases."""

    protocol: str
    name: str | None = None
    params: dict[str, Any] = field(default_factory=dict)
    stimuli: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _require_non_empty_string(self.protocol, "phase.protocol")
        if self.name is not None and not isinstance(self.name, str):
            raise BuilderDraftValidationError("phase.name must be a string when provided.")
        _require_dict(self.params, "phase.params")
        _require_dict(self.stimuli, "phase.stimuli")
        _resolve_trials(self.params)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "BuilderPhaseDraft":
        payload = _require_dict(data, "phase")
        return cls(
            protocol=_require_non_empty_string(payload.get("protocol", ""), "phase.protocol"),
            name=payload.get("name"),
            params=_require_dict(payload.get("params", {}), "phase.params"),
            stimuli=_require_dict(payload.get("stimuli", {}), "phase.stimuli"),
        )

    def to_dict(self, *, index: int) -> dict[str, Any]:
        params = dict(self.params)
        trials = _resolve_trials(params)
        params["n_trials"] = trials
        out: dict[str, Any] = {
            "name": self.name if self.name is not None else f"Phase {index}",
            "protocol": self.protocol,
            "params": params,
            "trials": trials,
            "stimuli": dict(self.stimuli),
        }
        return out


@dataclass(frozen=True)
class BuilderProgramDraft:
    """Program draft contract with protocol-mode convenience and phase-mode."""

    protocol: str | None = None
    params: dict[str, Any] = field(default_factory=dict)
    stimuli: dict[str, Any] = field(default_factory=dict)
    phases: tuple[BuilderPhaseDraft, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if self.protocol is not None:
            _require_non_empty_string(self.protocol, "program.protocol")
        _require_dict(self.params, "program.params")
        _require_dict(self.stimuli, "program.stimuli")
        for idx, phase in enumerate(self.phases):
            if not isinstance(phase, BuilderPhaseDraft):
                raise BuilderDraftValidationError(f"program.phases[{idx}] must be a BuilderPhaseDraft.")
        has_protocol = bool(self.protocol)
        has_phases = len(self.phases) > 0
        if has_protocol and has_phases:
            raise BuilderDraftValidationError("program draft must use either protocol mode or phases mode, not both.")
        if not has_protocol and not has_phases:
            raise BuilderDraftValidationError("program draft must define protocol mode or at least one phase.")

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "BuilderProgramDraft":
        payload = _require_dict(data, "experiment.program")
        phases_raw = payload.get("phases")
        phases: tuple[BuilderPhaseDraft, ...] = tuple()
        if phases_raw is not None:
            if not isinstance(phases_raw, list):
                raise BuilderDraftValidationError("program.phases must be an array when provided.")
            phases = tuple(BuilderPhaseDraft.from_dict(item) for item in phases_raw)
        return cls(
            protocol=payload.get("protocol"),
            params=_require_dict(payload.get("params", {}), "program.params"),
            stimuli=_require_dict(payload.get("stimuli", {}), "program.stimuli"),
            phases=phases,
        )

    def to_dict(self) -> dict[str, Any]:
        if self.phases:
            return {"phases": [phase.to_dict(index=idx) for idx, phase in enumerate(self.phases)]}
        protocol = _require_non_empty_string(self.protocol, "program.protocol")
        single = BuilderPhaseDraft(protocol=protocol, name="Phase 0", params=self.params, stimuli=self.stimuli)
        return {"phases": [single.to_dict(index=0)]}


@dataclass(frozen=True)
class BuilderLearningDraft:
    """Agent learning draft contract."""

    rule: str
    params: dict[str, Any] = field(default_factory=dict)
    attention: dict[str, Any] = field(
        default_factory=lambda: {"config": {"name": "none", "params": {}}, "initial": {}}
    )

    def __post_init__(self) -> None:
        _require_non_empty_string(self.rule, "agent.learning.rule")
        _require_dict(self.params, "agent.learning.params")
        _require_dict(self.attention, "agent.learning.attention")

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "BuilderLearningDraft":
        payload = _require_dict(data, "agent.learning")
        return cls(
            rule=_require_non_empty_string(payload.get("rule", ""), "agent.learning.rule"),
            params=_require_dict(payload.get("params", {}), "agent.learning.params"),
            attention=_require_dict(payload.get("attention", {"config": {"name": "none", "params": {}}, "initial": {}}), "agent.learning.attention"),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "rule": self.rule,
            "params": dict(self.params),
            "attention": dict(self.attention),
        }


@dataclass(frozen=True)
class BuilderAgentDraft:
    """Canonical agent draft contract."""

    name: str
    representation: dict[str, Any] | str
    learning: BuilderLearningDraft
    policy: dict[str, Any] | str | None = None

    def __post_init__(self) -> None:
        _require_non_empty_string(self.name, "agent.name")
        if not isinstance(self.representation, (dict, str)):
            raise BuilderDraftValidationError("agent.representation must be a string or object.")
        if not isinstance(self.learning, BuilderLearningDraft):
            raise BuilderDraftValidationError("agent.learning must be a BuilderLearningDraft.")
        if self.policy is not None and not isinstance(self.policy, (str, dict)):
            raise BuilderDraftValidationError("agent.policy must be a string or object when provided.")

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "BuilderAgentDraft":
        payload = _require_dict(data, "experiment.agent")
        learning_raw = payload.get("learning")
        if not isinstance(learning_raw, dict):
            raise BuilderDraftValidationError("agent.learning must be an object.")
        return cls(
            name=_require_non_empty_string(payload.get("name", ""), "agent.name"),
            representation=payload.get("representation", "vector_elemental"),
            learning=BuilderLearningDraft.from_dict(learning_raw),
            policy=payload.get("policy"),
        )

    def to_dict(self) -> dict[str, Any]:
        representation: dict[str, Any]
        if isinstance(self.representation, str):
            representation = {"name": self.representation, "params": {}}
        else:
            representation = dict(self.representation)
            if "name" not in representation:
                raise BuilderDraftValidationError("agent.representation.name is required when representation is an object.")
            if "params" not in representation:
                representation["params"] = {}
            if not isinstance(representation["params"], dict):
                raise BuilderDraftValidationError("agent.representation.params must be an object.")
        return {
            "name": self.name,
            "representation": representation,
            "learning": self.learning.to_dict(),
            "policy": self.policy,
        }


@dataclass(frozen=True)
class BuilderExperimentDraft:
    """Typed canonical draft contract for browser builder composition."""

    program: BuilderProgramDraft
    agent: BuilderAgentDraft
    runtime: BuilderRuntimeDraft = field(default_factory=BuilderRuntimeDraft)

    def __post_init__(self) -> None:
        if not isinstance(self.program, BuilderProgramDraft):
            raise BuilderDraftValidationError("experiment.program must be a BuilderProgramDraft.")
        if not isinstance(self.agent, BuilderAgentDraft):
            raise BuilderDraftValidationError("experiment.agent must be a BuilderAgentDraft.")
        if not isinstance(self.runtime, BuilderRuntimeDraft):
            raise BuilderDraftValidationError("experiment.runtime must be a BuilderRuntimeDraft.")

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "BuilderExperimentDraft":
        payload = _require_dict(data, "experiment")

        # Backward-compatible parse for older flat draft objects.
        if "program" not in payload and ("protocol" in payload or "phases" in payload):
            protocol = payload.get("protocol")
            phases = payload.get("phases")
            program_raw: dict[str, Any] = {}
            if phases is not None:
                program_raw["phases"] = phases
            if protocol is not None:
                program_raw["protocol"] = protocol
                program_raw["params"] = payload.get("params", {})
                program_raw["stimuli"] = payload.get("stimuli", {})
            payload = {
                "program": program_raw,
                "agent": {
                    "name": payload.get("agent"),
                    "representation": payload.get("representation"),
                    "learning": {
                        "rule": payload.get("learner"),
                        "params": {},
                        "attention": {"config": {"name": "none", "params": {}}, "initial": {}},
                    },
                    "policy": payload.get("policy"),
                },
                "runtime": payload.get("runtime", {}),
            }

        return cls(
            program=BuilderProgramDraft.from_dict(payload.get("program", {})),
            agent=BuilderAgentDraft.from_dict(payload.get("agent", {})),
            runtime=BuilderRuntimeDraft.from_dict(payload.get("runtime")),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "program": self.program.to_dict(),
            "agent": self.agent.to_dict(),
            "runtime": self.runtime.to_dict(),
        }
