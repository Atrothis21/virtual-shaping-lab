from __future__ import annotations

import pytest

from virtual_shaping_lab.vsl.agent.learning import LearnerBundle
from virtual_shaping_lab.vsl.agent.learning.operators import (
    AccumulatingEligibilityTraceOperator,
    FixedAttentionOperator,
    LinearStateValuePredictionOperator,
    RescorlaWagnerErrorOperator,
    RescorlaWagnerUpdateOperator,
)


def test_v3_18_10_bundle_uses_attention_modulated_update_inputs():
    bundle = LearnerBundle(
        predictor=LinearStateValuePredictionOperator(),
        error_operator=RescorlaWagnerErrorOperator(),
        update_operator=RescorlaWagnerUpdateOperator(),
        attention_operator=FixedAttentionOperator(default_alpha=0.25),
        step_size=0.1,
        state={"weights": {"tone": 0.0}},
    )

    out = bundle.step(features={"tone": 1.0}, reward=1.0, done=False)
    assert out.error == pytest.approx(1.0, abs=1e-12)
    assert out.update_features["tone"] == pytest.approx(0.25, abs=1e-12)
    assert out.state["weights"]["tone"] == pytest.approx(0.025, abs=1e-12)


def test_v3_18_10_bundle_uses_eligibility_trace_for_update_inputs():
    bundle = LearnerBundle(
        predictor=LinearStateValuePredictionOperator(),
        error_operator=RescorlaWagnerErrorOperator(),
        update_operator=RescorlaWagnerUpdateOperator(),
        eligibility_operator=AccumulatingEligibilityTraceOperator(),
        step_size=0.1,
        discount=0.9,
        trace_decay=0.8,
        state={"weights": {"tone": 0.0}},
    )

    out1 = bundle.step(features={"tone": 1.0}, reward=1.0, done=False)
    out2 = bundle.step(features={"tone": 1.0}, reward=1.0, done=False)

    assert out1.update_features["tone"] == pytest.approx(1.0, abs=1e-12)
    assert out2.update_features["tone"] == pytest.approx(1.72, abs=1e-12)
    assert out2.state["weights"]["tone"] > out1.state["weights"]["tone"]

