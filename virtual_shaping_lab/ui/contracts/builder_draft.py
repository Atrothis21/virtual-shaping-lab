"""Typed builder draft contracts for UI-authored experiment payloads."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


class BuilderDraftValidationError(ValueError):
    """Raised when a builder draft violates UI contract requirements."""


FIELD_DOCS: dict[str, str] = {
    "BuilderRuntimeDraft.seed": "Optional deterministic RNG seed for run reproducibility.",
    "BuilderRuntimeDraft.update_mode": "Runtime update granularity: 'trial' or 'tick'.",
    "BuilderRuntimeDraft.record_mode": "Record emission granularity: 'trial' or 'tick'.",
    "BuilderRuntimeDraft.strict_records": "Enable strict runtime-record validation.",
    "BuilderRuntimeDraft.debug": "Enable debug telemetry fields in emitted records.",
    "BuilderPhaseDraft.protocol": "Canonical phase/protocol key for this phase entry.",
    "BuilderPhaseDraft.name": "Optional display label for builder/editor surfaces.",
    "BuilderPhaseDraft.params": "Phase parameter object forwarded to runtime payload.",
    "BuilderPhaseDraft.stimuli": "Optional per-phase stimulus object.",
    "BuilderExperimentDraft.learner": "Learner key for experiment stack construction.",
    "BuilderExperimentDraft.agent": "Agent key for experiment stack construction.",
    "BuilderExperimentDraft.representation": "Representation key for experiment stack construction.",
    "BuilderExperimentDraft.policy": "Optional policy key/object for control layer selection.",
    "BuilderExperimentDraft.runtime": "Runtime draft settings for update/record/debug behavior.",
    "BuilderExperimentDraft.protocol": "Single-protocol mode key (mutually exclusive with phases).",
    "BuilderExperimentDraft.params": "Single-protocol mode params object.",
    "BuilderExperimentDraft.stimuli": "Single-protocol mode stimulus object.",
    "BuilderExperimentDraft.phases": "Phase-mode list (mutually exclusive with protocol mode).",
}


def _require_dict(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise BuilderDraftValidationError(f"{label} must be an object.")
    return value


@dataclass(frozen=True)
class BuilderRuntimeDraft:
    """Minimal runtime draft consumed by UI builder and translated to payload."""

    seed: int | None = None
    update_mode: str = "trial"
    record_mode: str = "trial"
    strict_records: bool = False
    debug: bool = False

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

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> "BuilderRuntimeDraft":
        if data is None:
            return cls()
        payload = _require_dict(data, "runtime")
        return cls(
            seed=payload.get("seed"),
            update_mode=str(payload.get("update_mode", "trial")),
            record_mode=str(payload.get("record_mode", "trial")),
            strict_records=bool(payload.get("strict_records", False)),
            debug=bool(payload.get("debug", False)),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "seed": self.seed,
            "update_mode": self.update_mode,
            "record_mode": self.record_mode,
            "strict_records": self.strict_records,
            "debug": self.debug,
        }


@dataclass(frozen=True)
class BuilderPhaseDraft:
    """Typed phase draft entry for phase-mode builder payloads."""

    protocol: str
    name: str | None = None
    params: dict[str, Any] = field(default_factory=dict)
    stimuli: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.protocol, str) or not self.protocol.strip():
            raise BuilderDraftValidationError("phase.protocol must be a non-empty string.")
        if self.name is not None and not isinstance(self.name, str):
            raise BuilderDraftValidationError("phase.name must be a string when provided.")
        _require_dict(self.params, "phase.params")
        _require_dict(self.stimuli, "phase.stimuli")

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "BuilderPhaseDraft":
        payload = _require_dict(data, "phase")
        return cls(
            protocol=str(payload.get("protocol", "")),
            name=payload.get("name"),
            params=_require_dict(payload.get("params", {}), "phase.params"),
            stimuli=_require_dict(payload.get("stimuli", {}), "phase.stimuli"),
        )

    def to_dict(self) -> dict[str, Any]:
        out: dict[str, Any] = {
            "protocol": self.protocol,
            "params": dict(self.params),
        }
        if self.name is not None:
            out["name"] = self.name
        if self.stimuli:
            out["stimuli"] = dict(self.stimuli)
        return out


@dataclass(frozen=True)
class BuilderExperimentDraft:
    """Typed experiment draft contract for browser builder composition."""

    learner: str
    agent: str
    representation: str
    policy: dict[str, Any] | str | None = None
    runtime: BuilderRuntimeDraft = field(default_factory=BuilderRuntimeDraft)
    protocol: str | None = None
    params: dict[str, Any] = field(default_factory=dict)
    stimuli: dict[str, Any] = field(default_factory=dict)
    phases: tuple[BuilderPhaseDraft, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if not isinstance(self.learner, str) or not self.learner.strip():
            raise BuilderDraftValidationError("experiment.learner must be a non-empty string.")
        if not isinstance(self.agent, str) or not self.agent.strip():
            raise BuilderDraftValidationError("experiment.agent must be a non-empty string.")
        if not isinstance(self.representation, str) or not self.representation.strip():
            raise BuilderDraftValidationError("experiment.representation must be a non-empty string.")
        if self.policy is not None and not isinstance(self.policy, (str, dict)):
            raise BuilderDraftValidationError("experiment.policy must be a string or object when provided.")
        _require_dict(self.params, "experiment.params")
        _require_dict(self.stimuli, "experiment.stimuli")
        if not isinstance(self.runtime, BuilderRuntimeDraft):
            raise BuilderDraftValidationError("experiment.runtime must be a BuilderRuntimeDraft.")
        for idx, phase in enumerate(self.phases):
            if not isinstance(phase, BuilderPhaseDraft):
                raise BuilderDraftValidationError(
                    f"experiment.phases[{idx}] must be a BuilderPhaseDraft."
                )

        has_protocol = isinstance(self.protocol, str) and bool(self.protocol.strip())
        has_phases = len(self.phases) > 0
        if has_protocol and has_phases:
            raise BuilderDraftValidationError(
                "experiment draft must use either protocol mode or phases mode, not both."
            )
        if not has_protocol and not has_phases:
            raise BuilderDraftValidationError(
                "experiment draft must define protocol mode or at least one phase."
            )

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "BuilderExperimentDraft":
        payload = _require_dict(data, "experiment")
        phases_raw = payload.get("phases")
        phases: tuple[BuilderPhaseDraft, ...] = tuple()
        if phases_raw is not None:
            if not isinstance(phases_raw, list):
                raise BuilderDraftValidationError("experiment.phases must be an array when provided.")
            phases = tuple(BuilderPhaseDraft.from_dict(item) for item in phases_raw)

        runtime = BuilderRuntimeDraft.from_dict(payload.get("runtime"))
        return cls(
            learner=str(payload.get("learner", "")),
            agent=str(payload.get("agent", "")),
            representation=str(payload.get("representation", "")),
            policy=payload.get("policy"),
            runtime=runtime,
            protocol=payload.get("protocol"),
            params=_require_dict(payload.get("params", {}), "experiment.params"),
            stimuli=_require_dict(payload.get("stimuli", {}), "experiment.stimuli"),
            phases=phases,
        )

    def to_dict(self) -> dict[str, Any]:
        out: dict[str, Any] = {
            "learner": self.learner,
            "agent": self.agent,
            "representation": self.representation,
            "runtime": self.runtime.to_dict(),
        }
        if self.policy is not None:
            out["policy"] = dict(self.policy) if isinstance(self.policy, dict) else self.policy
        if self.protocol:
            out["protocol"] = self.protocol
            if self.params:
                out["params"] = dict(self.params)
            if self.stimuli:
                out["stimuli"] = dict(self.stimuli)
        if self.phases:
            out["phases"] = [phase.to_dict() for phase in self.phases]
        return out
