from __future__ import annotations

import pytest

from virtual_shaping_lab.vsl.agent.learning import LearnerBundle, LearnerStepResult
from virtual_shaping_lab.vsl.agent.learning.operators import (
    LinearStateValuePredictionOperator,
    RescorlaWagnerErrorOperator,
    RescorlaWagnerUpdateOperator,
    TD0ErrorOperator,
)


def test_v3_18_5_learner_bundle_step_rw_order_and_numeric_path():
    bundle = LearnerBundle(
        predictor=LinearStateValuePredictionOperator(),
        error_operator=RescorlaWagnerErrorOperator(),
        update_operator=RescorlaWagnerUpdateOperator(),
        step_size=0.1,
        state={"weights": {"tone": 0.5}},
    )

    out = bundle.step(features={"tone": 1.0}, reward=1.0, done=False)

    assert isinstance(out, LearnerStepResult)
    assert out.prediction == pytest.approx(0.5, abs=1e-12)
    assert out.error == pytest.approx(0.5, abs=1e-12)
    assert out.state["weights"]["tone"] == pytest.approx(0.55, abs=1e-12)
    assert out.measurements["prediction"] == pytest.approx(0.5, abs=1e-12)
    assert out.measurements["error"] == pytest.approx(0.5, abs=1e-12)
    assert out.measurements["reward"] == pytest.approx(1.0, abs=1e-12)


def test_v3_18_5_learner_bundle_step_td0_uses_next_prediction_before_update():
    bundle = LearnerBundle(
        predictor=LinearStateValuePredictionOperator(),
        error_operator=TD0ErrorOperator(gamma=0.9),
        update_operator=RescorlaWagnerUpdateOperator(),
        step_size=0.2,
        state={"weights": {"tone": 0.4, "noise": 0.2}},
    )

    out = bundle.step(
        features={"tone": 1.0, "noise": 0.0},
        next_features={"tone": 0.0, "noise": 1.0},
        reward=0.7,
        done=False,
    )

    assert out.prediction == pytest.approx(0.4, abs=1e-12)
    assert out.next_prediction == pytest.approx(0.2, abs=1e-12)
    assert out.error == pytest.approx(0.48, abs=1e-12)
    assert out.state["weights"]["tone"] == pytest.approx(0.496, abs=1e-12)
    assert out.state["weights"]["noise"] == pytest.approx(0.2, abs=1e-12)


def test_v3_18_5_learner_bundle_step_invokes_attention_and_eligibility_hooks():
    class _Attention:
        def apply(self, *, attention_state, features, error):
            state = dict(attention_state or {})
            for key, value in features.items():
                state[key] = float(state.get(key, 0.0)) + float(value) * float(error)
            return state

    class _Eligibility:
        def apply(self, *, eligibility_state, features, discount, trace_decay):
            state = dict(eligibility_state or {})
            coeff = float(discount) * float(trace_decay)
            for key, value in features.items():
                state[key] = coeff * float(state.get(key, 0.0)) + float(value)
            return state

    bundle = LearnerBundle(
        predictor=LinearStateValuePredictionOperator(),
        error_operator=RescorlaWagnerErrorOperator(),
        update_operator=RescorlaWagnerUpdateOperator(),
        step_size=0.1,
        discount=0.9,
        trace_decay=0.8,
        attention_operator=_Attention(),
        eligibility_operator=_Eligibility(),
        state={"weights": {"tone": 0.0}},
    )

    out = bundle.step(features={"tone": 1.0}, reward=1.0, done=False)

    assert out.attention_state == {"tone": pytest.approx(1.0, abs=1e-12)}
    assert out.eligibility_state == {"tone": pytest.approx(1.0, abs=1e-12)}
    assert out.state["weights"]["tone"] == pytest.approx(0.1, abs=1e-12)


def test_v3_18_5_learner_bundle_step_order_is_predict_error_hooks_update():
    calls: list[str] = []

    class _Predict:
        def __call__(self, *, features, state=None):
            calls.append("predict")
            _ = features, state
            return 0.2

    class _Error:
        def __call__(self, *, reward, prediction, next_prediction=None, done=False):
            calls.append("error")
            _ = reward, prediction, next_prediction, done
            return 0.3

    class _Attention:
        def apply(self, *, attention_state, features, error):
            calls.append("attention")
            _ = attention_state, features, error
            return {}

    class _Eligibility:
        def apply(self, *, eligibility_state, features, discount, trace_decay):
            calls.append("eligibility")
            _ = eligibility_state, features, discount, trace_decay
            return {}

    class _Update:
        def __call__(self, *, state, features, error, step_size):
            calls.append("update")
            _ = features, error, step_size
            state["updated"] = True
            return state

    bundle = LearnerBundle(
        predictor=_Predict(),
        error_operator=_Error(),
        attention_operator=_Attention(),
        eligibility_operator=_Eligibility(),
        update_operator=_Update(),
        step_size=0.1,
        state={},
    )

    out = bundle.step(features={"tone": 1.0}, reward=1.0)

    assert out.state["updated"] is True
    assert calls == ["predict", "error", "attention", "eligibility", "update"]
