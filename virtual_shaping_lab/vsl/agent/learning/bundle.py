"""Executable learner bundle orchestration (V3.18.5 slice 4)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, MutableMapping

from .operators import (
    AttentionOperator,
    EligibilityOperator,
    ErrorOperator,
    NullAttentionOperator,
    NullEligibilityOperator,
    PredictionOperator,
    PredictionOutput,
    UpdateOperator,
    modulate_features_by_attention,
)


@dataclass(frozen=True)
class LearnerStepResult:
    """Per-step learner outputs persisted for measurement/reporting paths."""

    prediction_output: PredictionOutput
    prediction: float
    next_prediction: float | None
    error: float
    done: bool
    reward: float
    features: dict[str, float]
    next_features: dict[str, float] | None
    update_features: dict[str, float]
    state: dict[str, Any]
    attention_state: dict[str, float] | None
    eligibility_state: dict[str, float] | None
    measurements: dict[str, Any] = field(default_factory=dict)


def _coerce_features(features: Mapping[str, float]) -> dict[str, float]:
    return {str(key): float(value) for key, value in features.items()}


def _coerce_prediction_output(raw: Any) -> PredictionOutput:
    if isinstance(raw, PredictionOutput):
        return raw
    return PredictionOutput.from_state_value(float(raw))


@dataclass
class LearnerBundle:
    """
    Canonical executable learner step order:
    1) predict
    2) error
    3) optional attention/eligibility hooks
    4) update
    """

    predictor: PredictionOperator
    error_operator: ErrorOperator
    update_operator: UpdateOperator
    step_size: float
    discount: float = 0.0
    trace_decay: float = 0.0
    attention_operator: AttentionOperator = field(default_factory=NullAttentionOperator)
    eligibility_operator: EligibilityOperator = field(default_factory=NullEligibilityOperator)
    state: MutableMapping[str, Any] = field(default_factory=dict)
    attention_state: MutableMapping[str, float] | None = None
    eligibility_state: MutableMapping[str, float] | None = None

    def step(
        self,
        *,
        features: Mapping[str, float],
        reward: float,
        next_features: Mapping[str, float] | None = None,
        done: bool = False,
    ) -> LearnerStepResult:
        x = _coerce_features(features)

        prediction_output = _coerce_prediction_output(self.predictor(features=x, state=self.state))
        prediction = float(prediction_output.state_value)

        next_prediction: float | None = None
        next_x: dict[str, float] | None = None
        if next_features is not None:
            next_x = _coerce_features(next_features)
            next_output = _coerce_prediction_output(self.predictor(features=next_x, state=self.state))
            next_prediction = float(next_output.state_value)

        delta = float(
            self.error_operator(
                reward=float(reward),
                prediction=prediction,
                next_prediction=next_prediction,
                done=bool(done),
            )
        )

        attn_op = self.attention_operator
        self.attention_state = attn_op.apply(
            attention_state=self.attention_state,
            features=x,
            error=delta,
        )

        elig_op = self.eligibility_operator
        self.eligibility_state = elig_op.apply(
            eligibility_state=self.eligibility_state,
            features=x,
            discount=float(self.discount),
            trace_decay=float(self.trace_decay),
        )

        update_features = dict(x)
        if isinstance(self.eligibility_state, Mapping) and self.eligibility_state:
            update_features = {str(key): float(value) for key, value in self.eligibility_state.items()}
        if isinstance(self.attention_state, Mapping) and self.attention_state:
            update_features = modulate_features_by_attention(
                features=update_features,
                attention_state=self.attention_state,
            )

        self.state = self.update_operator(
            state=self.state,
            features=update_features,
            error=delta,
            step_size=float(self.step_size),
        )

        state_snapshot = dict(self.state)
        attention_snapshot = None if self.attention_state is None else dict(self.attention_state)
        eligibility_snapshot = None if self.eligibility_state is None else dict(self.eligibility_state)
        measurements = {
            "prediction": prediction,
            "next_prediction": next_prediction,
            "error": delta,
            "reward": float(reward),
            "done": bool(done),
            "update_features": dict(update_features),
            "action_values": dict(prediction_output.action_values),
            "metadata": dict(prediction_output.metadata),
        }
        return LearnerStepResult(
            prediction_output=prediction_output,
            prediction=prediction,
            next_prediction=next_prediction,
            error=delta,
            done=bool(done),
            reward=float(reward),
            features=x,
            next_features=next_x,
            update_features=dict(update_features),
            state=state_snapshot,
            attention_state=attention_snapshot,
            eligibility_state=eligibility_snapshot,
            measurements=measurements,
        )
