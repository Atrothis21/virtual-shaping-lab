from virtual_shaping_lab.agents.math_objects.attention_objects import build_attention_mechanism
from virtual_shaping_lab.agents.learners.attention_strategies import (
    AttentionContext,
    build_attention_strategy,
)


def test_static_attention_strategy_current_alpha_and_state_update():
    strategy = build_attention_strategy(
        "static",
        params={"default": 1.0, "overrides": {"tone": 0.6}},
    )
    alpha = strategy.current_alpha(("tone", "noise"))
    assert alpha["tone"] == 0.6
    assert alpha["noise"] == 1.0
    assert strategy.current_alpha_for_cues(["tone", "noise"]) == 0.8

    state = strategy.update_state(
        AttentionContext(
            active_features=("tone", "noise"),
            feature_contributions={"tone": 0.4, "noise": 0.2},
            total_prediction=0.6,
            reward=1.0,
            prediction_error=0.4,
        )
    )
    assert state.alpha_by_feature == {"tone": 0.6, "noise": 1.0}


def test_attention_mechanism_builder_returns_contract_implementation():
    mechanism = build_attention_mechanism(
        "static",
        params={"default": 1.0, "overrides": {"tone": 0.6}},
    )
    assert callable(getattr(mechanism, "current_alpha", None))
    assert callable(getattr(mechanism, "update_state", None))
    assert mechanism.current_alpha(("tone",))["tone"] == 0.6


def test_none_attention_strategy_is_unity():
    strategy = build_attention_strategy("none")
    assert strategy.current_alpha_for_cues("tone") == 1.0
    assert strategy.current_alpha(("tone",)) == {"tone": 1.0}


def test_pearce_hall_updates_and_preserves_bounds():
    strategy = build_attention_strategy(
        "pearce_hall",
        params={"default": 0.4, "eta": 0.5},
    )
    before = strategy.current_alpha(("tone",))["tone"]
    assert before == 0.4

    after_state = strategy.update_state(
        AttentionContext(
            active_features=("tone",),
            feature_contributions={"tone": 0.2},
            total_prediction=0.2,
            reward=1.0,
            prediction_error=1.2,  # clipped to 1.0 target
        )
    )
    assert 0.0 <= after_state.alpha_by_feature["tone"] <= 1.0
    assert after_state.alpha_by_feature["tone"] > before


def test_mackintosh_relative_predictiveness_shift():
    strategy = build_attention_strategy(
        "mackintosh",
        params={"default": 0.5, "kappa": 0.2},
    )
    state = strategy.update_state(
        AttentionContext(
            active_features=("tone", "noise"),
            feature_contributions={"tone": 0.8, "noise": 0.1},
            total_prediction=0.9,
            reward=1.0,
            prediction_error=0.1,
        )
    )
    assert 0.0 <= state.alpha_by_feature["tone"] <= 1.0
    assert 0.0 <= state.alpha_by_feature["noise"] <= 1.0
    assert state.alpha_by_feature["tone"] > state.alpha_by_feature["noise"]
