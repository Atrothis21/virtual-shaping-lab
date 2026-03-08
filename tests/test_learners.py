import numpy as np
import pytest

from agents.learners.base import BaseLearner
from agents.learners.q_learner import QLearner
from agents.learners.rescorla_wagner import RescorlaWagnerLearner
from agents.learners.td_value import TDValueLearner
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
