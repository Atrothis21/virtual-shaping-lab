"""Executable learner presets for V3.18.5 core bundle."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, MutableMapping

from .bundle import LearnerBundle
from .operators.attention import MackintoshAttentionOperator, PearceHallAttentionOperator
from .operators.eligibility import AccumulatingEligibilityTraceOperator
from .operators.error import RescorlaWagnerErrorOperator, TD0ErrorOperator
from .operators.prediction import LinearStateValuePredictionOperator
from .operators.update import RescorlaWagnerUpdateOperator, TD0UpdateOperator
from .presets import expand_learner_preset
from .spec import LearnerSpec


@dataclass(frozen=True)
class ExecutableLearnerPreset:
    """Resolved executable learner preset payload."""

    preset_name: str
    learner_spec: LearnerSpec
    bundle: LearnerBundle


def executable_learner_preset_names() -> list[str]:
    return ["rescorla_wagner", "td0", "pearce_hall_rw", "mackintosh_rw", "td_lambda"]


def _copy_state(state: Mapping[str, Any] | None) -> MutableMapping[str, Any]:
    if not isinstance(state, Mapping):
        return {"weights": {}}
    copied = dict(state)
    raw_weights = copied.get("weights")
    if isinstance(raw_weights, Mapping):
        copied["weights"] = {str(k): float(v) for k, v in raw_weights.items()}
    else:
        copied["weights"] = {}
    return copied


def _coerce_learner_spec(spec: LearnerSpec | Mapping[str, Any]) -> LearnerSpec:
    if isinstance(spec, LearnerSpec):
        return spec
    if isinstance(spec, Mapping):
        return LearnerSpec.from_dict(dict(spec))
    raise TypeError("spec must be LearnerSpec or object payload.")


def build_executable_learner_preset(
    preset_name: str,
    *,
    step_size: float = 0.1,
    gamma: float = 0.0,
    trace_decay: float = 0.0,
    state: Mapping[str, Any] | None = None,
) -> ExecutableLearnerPreset:
    """
    Materialize executable core preset bundles.

    Supported presets in V3.18.10:
    - rescorla_wagner
    - td0
    - pearce_hall_rw
    - mackintosh_rw
    - td_lambda
    """
    requested = str(preset_name).strip()
    if requested == "rescorla_wagner":
        spec = expand_learner_preset("rescorla_wagner")
        bundle = LearnerBundle(
            predictor=LinearStateValuePredictionOperator(),
            error_operator=RescorlaWagnerErrorOperator(),
            update_operator=RescorlaWagnerUpdateOperator(),
            step_size=float(step_size),
            discount=float(gamma),
            trace_decay=float(trace_decay),
            state=_copy_state(state),
        )
        return ExecutableLearnerPreset(
            preset_name=requested,
            learner_spec=spec,
            bundle=bundle,
        )

    if requested == "td0":
        spec = expand_learner_preset("td0")
        bundle = LearnerBundle(
            predictor=LinearStateValuePredictionOperator(),
            error_operator=TD0ErrorOperator(gamma=float(gamma)),
            update_operator=TD0UpdateOperator(),
            step_size=float(step_size),
            discount=float(gamma),
            trace_decay=float(trace_decay),
            state=_copy_state(state),
        )
        return ExecutableLearnerPreset(
            preset_name=requested,
            learner_spec=spec,
            bundle=bundle,
        )

    if requested == "pearce_hall_rw":
        spec = LearnerSpec(
            trace="none",
            predictor="state_value",
            error="rw_error",
            attention="pearce_hall",
            updater="attention_delta_rule",
            policy="none",
            metadata={"preset_name": requested, "preset_version": "3.6.0"},
        )
        bundle = LearnerBundle(
            predictor=LinearStateValuePredictionOperator(),
            error_operator=RescorlaWagnerErrorOperator(),
            update_operator=RescorlaWagnerUpdateOperator(),
            attention_operator=PearceHallAttentionOperator(),
            step_size=float(step_size),
            discount=float(gamma),
            trace_decay=float(trace_decay),
            state=_copy_state(state),
        )
        return ExecutableLearnerPreset(
            preset_name=requested,
            learner_spec=spec,
            bundle=bundle,
        )

    if requested == "mackintosh_rw":
        spec = LearnerSpec(
            trace="none",
            predictor="state_value",
            error="rw_error",
            attention="mackintosh",
            updater="attention_delta_rule",
            policy="none",
            metadata={"preset_name": requested, "preset_version": "3.6.0"},
        )
        bundle = LearnerBundle(
            predictor=LinearStateValuePredictionOperator(),
            error_operator=RescorlaWagnerErrorOperator(),
            update_operator=RescorlaWagnerUpdateOperator(),
            attention_operator=MackintoshAttentionOperator(),
            step_size=float(step_size),
            discount=float(gamma),
            trace_decay=float(trace_decay),
            state=_copy_state(state),
        )
        return ExecutableLearnerPreset(
            preset_name=requested,
            learner_spec=spec,
            bundle=bundle,
        )

    if requested == "td_lambda":
        spec = expand_learner_preset("td_lambda_classical")
        bundle = LearnerBundle(
            predictor=LinearStateValuePredictionOperator(),
            error_operator=TD0ErrorOperator(gamma=float(gamma)),
            update_operator=TD0UpdateOperator(),
            eligibility_operator=AccumulatingEligibilityTraceOperator(),
            step_size=float(step_size),
            discount=float(gamma),
            trace_decay=float(trace_decay),
            state=_copy_state(state),
        )
        return ExecutableLearnerPreset(
            preset_name=requested,
            learner_spec=spec,
            bundle=bundle,
        )

    known = ", ".join(executable_learner_preset_names())
    raise ValueError(f"Unknown executable learner preset '{preset_name}'. Known presets: {known}")


def build_executable_learner_from_spec(
    spec: LearnerSpec | Mapping[str, Any],
    *,
    step_size: float = 0.1,
    gamma: float = 0.0,
    trace_decay: float = 0.0,
    state: Mapping[str, Any] | None = None,
) -> ExecutableLearnerPreset:
    """
    Materialize executable learner bundle directly from legal symbolic learner spec.

    V3.18.10 supports executable mapping for:
    - RW tuple: (none, state_value, rw_error, fixed, delta_rule, none)
    - TD0 tuple: (none, state_value, td_error, fixed, delta_rule, none)
    - Pearce-Hall RW tuple
    - Mackintosh RW tuple
    - TD-lambda classical tuple
    """
    learner_spec = _coerce_learner_spec(spec)
    if learner_spec.attention in {"pearce_hall", "mackintosh", "hybrid_attention"} and learner_spec.updater != "attention_delta_rule":
        raise ValueError(
            "[LGR_E_EXECUTABLE_ATTENTION_UPDATER] Non-fixed attention requires updater='attention_delta_rule' for executable mapping."
        )
    if learner_spec.trace in {"eligibility", "recency"} and learner_spec.updater not in {"trace_delta_rule", "attention_delta_rule"}:
        raise ValueError(
            "[LGR_E_EXECUTABLE_TRACE_UPDATER] Trace-enabled executable mapping requires updater in {'trace_delta_rule', 'attention_delta_rule'}."
        )

    signature = (
        learner_spec.trace,
        learner_spec.predictor,
        learner_spec.error,
        learner_spec.attention,
        learner_spec.updater,
        learner_spec.policy,
    )
    rw_sig = ("none", "state_value", "rw_error", "fixed", "delta_rule", "none")
    td0_sig = ("none", "state_value", "td_error", "fixed", "delta_rule", "none")
    ph_rw_sig = ("none", "state_value", "rw_error", "pearce_hall", "attention_delta_rule", "none")
    mack_rw_sig = ("none", "state_value", "rw_error", "mackintosh", "attention_delta_rule", "none")
    td_lambda_sig = ("eligibility", "state_value", "td_error", "fixed", "trace_delta_rule", "none")
    if signature == rw_sig:
        return build_executable_learner_preset(
            "rescorla_wagner",
            step_size=step_size,
            gamma=gamma,
            trace_decay=trace_decay,
            state=state,
        )
    if signature == td0_sig:
        return build_executable_learner_preset(
            "td0",
            step_size=step_size,
            gamma=gamma,
            trace_decay=trace_decay,
            state=state,
        )
    if signature == ph_rw_sig:
        return build_executable_learner_preset(
            "pearce_hall_rw",
            step_size=step_size,
            gamma=gamma,
            trace_decay=trace_decay,
            state=state,
        )
    if signature == mack_rw_sig:
        return build_executable_learner_preset(
            "mackintosh_rw",
            step_size=step_size,
            gamma=gamma,
            trace_decay=trace_decay,
            state=state,
        )
    if signature == td_lambda_sig:
        return build_executable_learner_preset(
            "td_lambda",
            step_size=step_size,
            gamma=gamma,
            trace_decay=trace_decay,
            state=state,
        )
    raise ValueError(
        "[LGR_E_EXECUTABLE_UNSUPPORTED_SPEC] Symbolic learner spec is legal but does not map "
        "to a V3.18.10 executable core preset."
    )
