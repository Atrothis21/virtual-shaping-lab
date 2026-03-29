"""Learner instantiation boundary from grammar tuples to executable contracts.

V3.18.0 slice 3 scope:
- enforce learner legality before materialization
- provide typed placeholders for optional operators (A, E)
- expose a deterministic boundary payload for runtime assembly
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping

from .adapters import grammar_to_runtime_learner_config
from .resolve import resolve_learner_spec
from .spec import LearnerSpec
from .validation import LearnerSpecValidationError
from virtual_shaping_lab.vsl.spec.contracts import LearnerSpec as RuntimeLearnerConfig


LEARNER_INSTANTIATION_FAILURES: dict[str, str] = {
    "INST_E_INVALID_SPEC_INPUT": "Learner spec input must be LearnerSpec or object payload.",
    "INST_E_LEGALITY": "Learner spec failed legality validation before materialization.",
    "INST_E_BOUNDARY_RESOLUTION": "Learner boundary resolution failed for legacy/runtime inputs.",
}


@dataclass
class LearnerInstantiationError(ValueError):
    code: str
    message: str
    details: dict[str, Any] = field(default_factory=dict)

    def __str__(self) -> str:
        return f"[{self.code}] {self.message}"


@dataclass(frozen=True)
class OperatorHandle:
    slot: str
    variant: str
    params: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.slot, str) or not self.slot.strip():
            raise ValueError("OperatorHandle.slot must be a non-empty string.")
        if not isinstance(self.variant, str) or not self.variant.strip():
            raise ValueError("OperatorHandle.variant must be a non-empty string.")
        if not isinstance(self.params, dict):
            raise ValueError("OperatorHandle.params must be an object.")


@dataclass(frozen=True)
class NullAttentionOperator:
    slot: str = "A"
    variant: str = "null_attention"


@dataclass(frozen=True)
class NullTraceOperator:
    slot: str = "E"
    variant: str = "null_trace"


@dataclass(frozen=True)
class LearnerInstantiationArtifact:
    learner_spec: LearnerSpec
    runtime_config: RuntimeLearnerConfig
    predictor_operator: OperatorHandle
    error_operator: OperatorHandle
    updater_operator: OperatorHandle
    policy_operator: OperatorHandle
    attention_operator: OperatorHandle | NullAttentionOperator
    trace_operator: OperatorHandle | NullTraceOperator


def _coerce_learner_spec(spec: LearnerSpec | Mapping[str, Any]) -> LearnerSpec:
    if isinstance(spec, LearnerSpec):
        return spec
    if isinstance(spec, Mapping):
        try:
            return LearnerSpec.from_dict(dict(spec))
        except (LearnerSpecValidationError, ValueError, TypeError) as exc:
            raise LearnerInstantiationError(
                "INST_E_LEGALITY",
                LEARNER_INSTANTIATION_FAILURES["INST_E_LEGALITY"],
                details={"reason": str(exc)},
            ) from exc
    raise LearnerInstantiationError(
        "INST_E_INVALID_SPEC_INPUT",
        LEARNER_INSTANTIATION_FAILURES["INST_E_INVALID_SPEC_INPUT"],
    )


def instantiate_learner_contracts(
    spec: LearnerSpec | Mapping[str, Any],
    *,
    attention_initial: Mapping[str, Any] | None = None,
) -> LearnerInstantiationArtifact:
    """
    Materialize typed learner boundary contracts from canonical grammar spec.
    """
    learner_spec = _coerce_learner_spec(spec)
    runtime_config = grammar_to_runtime_learner_config(
        learner_spec,
        attention_initial=attention_initial,
    )

    attention_operator: OperatorHandle | NullAttentionOperator
    if learner_spec.attention == "fixed":
        attention_operator = NullAttentionOperator()
    else:
        attention_operator = OperatorHandle(slot="A", variant=learner_spec.attention)

    trace_operator: OperatorHandle | NullTraceOperator
    if learner_spec.trace == "none":
        trace_operator = NullTraceOperator()
    else:
        trace_operator = OperatorHandle(slot="E", variant=learner_spec.trace)

    return LearnerInstantiationArtifact(
        learner_spec=learner_spec,
        runtime_config=runtime_config,
        predictor_operator=OperatorHandle(slot="P", variant=learner_spec.predictor),
        error_operator=OperatorHandle(slot="Err", variant=learner_spec.error),
        updater_operator=OperatorHandle(slot="Update", variant=learner_spec.updater),
        policy_operator=OperatorHandle(slot="Pi", variant=learner_spec.policy),
        attention_operator=attention_operator,
        trace_operator=trace_operator,
    )


def instantiate_learner_from_boundary(
    *,
    learner_rule: Any,
    policy_config: Any,
    learning_config: Mapping[str, Any] | None = None,
    metadata: Mapping[str, Any] | None = None,
    attention_initial: Mapping[str, Any] | None = None,
) -> LearnerInstantiationArtifact:
    """
    Resolve learner boundary inputs and materialize typed learner contracts.
    """
    try:
        resolved = resolve_learner_spec(
            learner_rule=learner_rule,
            policy_config=policy_config,
            learning_config=learning_config,
            metadata=metadata,
        )
    except Exception as exc:
        raise LearnerInstantiationError(
            "INST_E_BOUNDARY_RESOLUTION",
            LEARNER_INSTANTIATION_FAILURES["INST_E_BOUNDARY_RESOLUTION"],
            details={"reason": str(exc)},
        ) from exc

    return instantiate_learner_contracts(resolved, attention_initial=attention_initial)
