"""Executable learner presets for V3.18.5 core bundle."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, MutableMapping

from .bundle import LearnerBundle
from .presets import expand_learner_preset
from .spec import LearnerSpec
from .operators import (
    LinearStateValuePredictionOperator,
    RescorlaWagnerErrorOperator,
    RescorlaWagnerUpdateOperator,
    TD0ErrorOperator,
    TD0UpdateOperator,
)


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

