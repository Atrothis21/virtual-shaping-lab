import numpy as np
import pytest

from agents.learners.attention_strategies import AttentionContext, build_attention_strategy
from agents.learners.base import BaseLearner
from domain.types import EncodedState, Transition


class _DummyLearner(BaseLearner):
    def update(self, transition: Transition) -> None:
        return None

    def value(self, state: EncodedState, action=None) -> float:
        return float(np.sum(state.x))


def _ctx(active_features=("f0", "f1")):
    return AttentionContext(
        active_features=tuple(active_features),
        feature_contributions={str(k): 0.2 for k in active_features},
        total_prediction=0.5,
        reward=1.0,
        prediction_error=0.4,
    )


def test_attention_strategy_resolution_rejects_unknown_name():
    with pytest.raises(ValueError, match="Unsupported attention strategy"):
        build_attention_strategy("not_a_strategy")


def test_attention_vectors_are_bounded_in_unit_interval():
    strategies = [
        build_attention_strategy("none"),
        build_attention_strategy("static", params={"default": 2.0, "overrides": {"f0": -1.0}}),
        build_attention_strategy("pearce_hall", params={"default": -2.0, "eta": 2.0}),
        build_attention_strategy("mackintosh", params={"default": 2.5, "kappa": -1.0}),
    ]
    for strategy in strategies:
        state = strategy.update_state(_ctx())
        alpha = strategy.current_alpha(("f0", "f1"))
        for v in alpha.values():
            assert 0.0 <= float(v) <= 1.0
        for v in state.alpha_by_feature.values():
            assert 0.0 <= float(v) <= 1.0


def test_attention_vector_shape_matches_active_features():
    strategy = build_attention_strategy("pearce_hall", params={"default": 0.5, "eta": 0.2})
    strategy.update_state(_ctx(active_features=("f0", "f1", "f2")))
    alpha = strategy.current_alpha(("f0", "f1", "f2"))
    assert set(alpha.keys()) == {"f0", "f1", "f2"}
    assert len(alpha) == 3


def test_diagonal_modulation_equivalence_for_aligned_feature_basis():
    strategy = build_attention_strategy(
        "static",
        params={"default": 1.0, "overrides": {"f0": 0.5, "f1": 0.25, "f2": 1.0}},
    )
    x = np.asarray([2.0, 4.0, 6.0], dtype=float)
    features = ("f0", "f1", "f2")
    alpha = strategy.current_alpha(features)
    a_vec = np.asarray([alpha[f] for f in features], dtype=float)
    lhs = a_vec * x
    rhs = np.diag(a_vec) @ x
    np.testing.assert_allclose(lhs, rhs, atol=1e-12)


def test_base_learner_attention_modulated_state_preserves_vector_codomain():
    learner = _DummyLearner(alpha=0.1, gamma=0.0)
    learner.set_attention_map({"tone": 0.5})
    transition = Transition(
        s=EncodedState(x=np.asarray([1.0, 2.0, 3.0], dtype=float)),
        r=1.0,
        metadata={"cue_labels": ["tone"]},
    )
    x_mod = learner.attention_modulated_state(
        transition,
        total_prediction=0.0,
        prediction_error=1.0,
        feature_contributions={"f0": 0.0, "f1": 0.0, "f2": 0.0},
    )
    assert isinstance(x_mod, np.ndarray)
    assert x_mod.shape == transition.s.x.shape

