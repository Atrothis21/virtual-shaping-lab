from __future__ import annotations

import pytest

from virtual_shaping_lab.vsl.agent.learning.operators import (
    AttentionOperator,
    FixedAttentionOperator,
    MackintoshAttentionOperator,
    PearceHallAttentionOperator,
    RescorlaWagnerErrorOperator,
    RescorlaWagnerUpdateOperator,
    modulate_features_by_attention,
)


def test_v3_18_10_fixed_attention_operator_contract():
    op = FixedAttentionOperator(default_alpha=1.0)
    assert isinstance(op, AttentionOperator)
    out = op.apply(attention_state=None, features={"tone": 1.0, "noise": 0.2}, error=0.8)
    assert out == {"tone": pytest.approx(1.0, abs=1e-12), "noise": pytest.approx(1.0, abs=1e-12)}


def test_v3_18_10_pearce_hall_attention_tracks_unsigned_error():
    op = PearceHallAttentionOperator(default_alpha=0.2, kappa=0.5)
    out = op.apply(attention_state={"tone": 0.2}, features={"tone": 1.0}, error=0.6)
    assert out == {"tone": pytest.approx(0.4, abs=1e-12)}


def test_v3_18_10_mackintosh_attention_prefers_higher_predictiveness_features():
    op = MackintoshAttentionOperator(default_alpha=0.5, kappa=0.1)
    out = op.apply(
        attention_state={"tone": 0.5, "noise": 0.5},
        features={"tone": 1.0, "noise": 0.1},
        error=0.8,
    )
    assert out["tone"] > 0.5
    assert out["noise"] < 0.5


def test_v3_18_10_attention_modulates_update_inputs_not_error_semantics():
    features = {"tone": 1.0}
    attention_state = {"tone": 0.25}
    error_op = RescorlaWagnerErrorOperator()
    update_op = RescorlaWagnerUpdateOperator()

    error_plain = error_op(reward=1.0, prediction=0.3)
    error_with_attention_context = error_op(reward=1.0, prediction=0.3)
    assert error_plain == pytest.approx(error_with_attention_context, abs=1e-12)

    modulated = modulate_features_by_attention(features=features, attention_state=attention_state)
    state_plain = {"weights": {"tone": 0.0}}
    state_modulated = {"weights": {"tone": 0.0}}

    update_op(state=state_plain, features=features, error=error_plain, step_size=0.1)
    update_op(state=state_modulated, features=modulated, error=error_plain, step_size=0.1)

    assert state_plain["weights"]["tone"] == pytest.approx(0.07, abs=1e-12)
    assert state_modulated["weights"]["tone"] == pytest.approx(0.0175, abs=1e-12)
    assert state_modulated["weights"]["tone"] < state_plain["weights"]["tone"]

