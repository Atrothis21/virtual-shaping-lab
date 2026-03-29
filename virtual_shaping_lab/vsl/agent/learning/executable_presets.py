"""Executable learner presets for V3.18.5 core bundle."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, MutableMapping

from .bundle import LearnerBundle
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
    return ["rescorla_wagner", "td0"]


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

    Supported presets in V3.18.5:
    - rescorla_wagner
    - td0
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

    V3.18.5 supports executable mapping for:
    - RW tuple: (none, state_value, rw_error, fixed, delta_rule, none)
    - TD0 tuple: (none, state_value, td_error, fixed, delta_rule, none)
    """
    learner_spec = _coerce_learner_spec(spec)
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
    raise ValueError(
        "[LGR_E_EXECUTABLE_UNSUPPORTED_SPEC] Symbolic learner spec is legal but does not map "
        "to a V3.18.5 executable core preset."
    )
