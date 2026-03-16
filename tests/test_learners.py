import numpy as np
import pytest

from agents.math_objects.attention_objects import build_attention_mechanism
from agents.math_objects.prediction_error_objects import (
    RescorlaWagnerPredictionError,
    TD0PredictionError,
)
from agents.learners.attention_strategies import AttentionContext
from agents.learners.base import BaseLearner
from agents.learners.q_learner import QLearner
from agents.learners.rescorla_wagner import RescorlaWagnerLearner
from agents.learners.td_value import TDValueLearner
from agents.representations.observation import make_observation
from agents.representations.vector_elemental import VectorElementalRepresentation
from domain.types import EncodedState, Transition


class CoverageDummyLearner(BaseLearner):
    def __init__(self, alpha=0.1, gamma=0.9):
        super().__init__(alpha=alpha, gamma=gamma)
        self.last = None

    def update(self, transition: Transition) -> None:
        self.last = transition

    def value(self, state: EncodedState, action=None) -> float:
        return float(np.sum(state.x))


class CoverageBadLearner(BaseLearner):
    def update(self, transition: Transition) -> None:
        return super().update(transition)

    def value(self, state: EncodedState, action=None) -> float:
        return super().value(state, action)


def s(vec):
    return EncodedState(x=np.asarray(vec, dtype=float))


def t(state, reward, action=None, next_state=None, done=False, metadata=None):
    return Transition(
        s=state,
        r=float(reward),
        a=action,
        s_next=next_state,
        done=done,
        metadata=metadata or {},
    )


def test_base_learner_hooks():
    learner = CoverageDummyLearner(alpha=0.1, gamma=0.9)
    state = s([1.0, 2.0])
    learner.update(t(state, 1.0))

    assert learner.value(state) == 3.0
    assert learner.expects_action() is False
    assert learner.start_episode() is None
    assert learner.end_episode() is None
    assert learner.get_parameters() == {}
    assert learner.last is not None

    bad = CoverageBadLearner(alpha=0.1, gamma=0.9)
    with pytest.raises(NotImplementedError):
        bad.update(t(state, 1.0))
    with pytest.raises(NotImplementedError):
        bad.value(state)


def test_prediction_error_rule_objects_match_expected_formulas():
    rw = RescorlaWagnerPredictionError()
    weights = np.asarray([0.2, 0.0], dtype=float)
    state = np.asarray([1.0, 0.0], dtype=float)
    assert rw.compute(state=state, reward=1.0, parameters=weights) == pytest.approx(0.8)

    td0 = TD0PredictionError(gamma=0.5)
    next_state = np.asarray([1.0, 0.0], dtype=float)
    assert td0.compute(
        state=state,
        reward=1.0,
        next_state=next_state,
        parameters=weights,
    ) == pytest.approx(0.9)


def test_attention_mechanism_builder_returns_math_object_contract():
    mechanism = build_attention_mechanism("pearce_hall", params={"default": 0.4, "eta": 0.5})
    assert callable(getattr(mechanism, "current_alpha", None))
    assert callable(getattr(mechanism, "update_state", None))
    state = mechanism.update_state(
        AttentionContext(
            active_features=("tone",),
            feature_contributions={"tone": 0.2},
            total_prediction=0.2,
            reward=1.0,
            prediction_error=0.6,
        )
    )
    assert 0.0 <= state.alpha_by_feature["tone"] <= 1.0


def test_rescorla_wagner_update_paths():
    learner = RescorlaWagnerLearner(state_dim=2, alpha=0.5)
    state = s([1.0, 0.0])
    learner.update(t(state, reward=1.0))
    assert learner.value(state) > 0

    salience = np.asarray([0.5, 0.5])
    learner2 = RescorlaWagnerLearner(state_dim=2, alpha=0.5, salience=salience)
    learner2.update(t(state, reward=1.0))
    assert learner2.value(state) > 0

    learner2.update(t(state, reward=1.0, metadata={"cue_labels": ["tone"]}))
    assert learner2.value(state) > 0


def test_rescorla_wagner_attention_modulated_input_path():
    learner = RescorlaWagnerLearner(state_dim=2, alpha=0.5)
    learner.set_attention_map({"tone": 0.5})
    state = s([1.0, 0.0])
    learner.update(t(state, reward=1.0, metadata={"cue_labels": ["tone"]}))
    # canonical update path: w += alpha * delta * (A_t ⊙ x_t)
    # here: 0 + 0.5 * 1.0 * (0.5 * 1.0) = 0.25
    assert learner.weights[0] == pytest.approx(0.25, abs=1e-12)
    diagnostics = learner.attention_diagnostics(cue_labels=["tone"])
    assert "alpha_by_stimulus" in diagnostics
    assert "mean_alpha" in diagnostics
    assert "prediction_error" in diagnostics


def test_td_value_update_paths():
    learner = TDValueLearner(state_dim=2, alpha=0.5, gamma=0.9)
    state = s([1.0, 0.0])
    next_state = s([0.5, 0.0])
    learner.update(t(state, reward=1.0, next_state=next_state, done=False))
    learner.update(t(state, reward=1.0, next_state=None, done=True))

    salience = np.asarray([0.5, 0.5])
    learner2 = TDValueLearner(state_dim=2, alpha=0.5, gamma=0.9, salience=salience)
    learner2.update(t(state, reward=1.0, next_state=next_state, done=False))
    learner2.update(t(state, reward=1.0, metadata={"cue_labels": ["tone"]}))


def test_qlearner_paths():
    learner = QLearner(state_dim=2, actions=[0, 1], alpha=0.5, gamma=0.9)
    state = s([1.0, 0.0])
    next_state = s([0.5, 0.0])

    assert learner.expects_action() is True
    assert learner.value(state) >= 0
    assert learner.value(state, action=0) >= 0

    with pytest.raises(ValueError):
        learner.update(t(state, reward=1.0, action=None, next_state=next_state))

    learner.update(t(state, reward=1.0, action=0, next_state=next_state, done=False))
    learner.update(t(state, reward=1.0, action=0, next_state=None, done=True))

    learner.salience = np.asarray([1.0, 1.0])
    learner.update(t(state, reward=1.0, action=0, next_state=next_state, done=False))

    learner.update(t(state, reward=1.0, action=1, metadata={"cue_labels": ["tone"]}))
    assert "weights" in learner.get_parameters()


def test_learner_salience_vector_does_not_reweight_updates():
    state = s([1.0, 0.0])

    base = RescorlaWagnerLearner(state_dim=2, alpha=0.5, salience=None)
    with_salience = RescorlaWagnerLearner(
        state_dim=2,
        alpha=0.5,
        salience=np.asarray([0.1, 1.0], dtype=float),
    )

    base.update(t(state, reward=1.0))
    with_salience.update(t(state, reward=1.0))
    np.testing.assert_allclose(base.weights, with_salience.weights)


def test_qlearner_deterministic_update_fixture():
    learner = QLearner(state_dim=2, actions=["left", "right"], alpha=0.5, gamma=0.0)
    state = s([1.0, 0.0])

    learner.update(t(state, reward=1.0, action="left", next_state=None, done=True))
    assert learner.value(state, action="left") == pytest.approx(0.5, abs=1e-12)

    learner.update(t(state, reward=-1.0, action="left", next_state=None, done=True))
    assert learner.value(state, action="left") == pytest.approx(-0.25, abs=1e-12)


def test_td_value_deterministic_update_fixture():
    learner = TDValueLearner(state_dim=2, alpha=0.5, gamma=0.5)
    state = s([1.0, 0.0])
    next_state = s([1.0, 0.0])

    learner.update(t(state, reward=1.0, next_state=next_state, done=False))
    assert learner.value(state) == pytest.approx(0.5, abs=1e-12)

    learner.update(t(state, reward=0.0, next_state=next_state, done=False))
    assert learner.value(state) == pytest.approx(0.375, abs=1e-12)


def test_temporal_basis_and_prediction_error_rule_interact_via_bootstrap():
    rep = VectorElementalRepresentation(
        params={
            "stimuli": ["tone"],
            "include_global": True,
            "include_context": False,
            "temporal_basis": {
                "enabled": True,
                "variant": "identity",
                "dimension": 1,
            },
        }
    )
    current = rep.encode(make_observation(["tone"], "A", t_s=0.0))
    next_state = rep.encode(make_observation(["tone"], "A", t_s=1.0))

    rw = RescorlaWagnerLearner(state_dim=rep.dimension, alpha=0.5)
    td = TDValueLearner(state_dim=rep.dimension, alpha=0.5, gamma=0.5)
    rw.weights = np.asarray([0.0, 2.0], dtype=float)
    td.weights = np.asarray([0.0, 2.0], dtype=float)

    transition = t(current, reward=0.0, next_state=next_state, done=False)
    rw.update(transition)
    td.update(transition)

    assert rw.weights[0] == pytest.approx(0.0)
    assert td.weights[0] > rw.weights[0]
