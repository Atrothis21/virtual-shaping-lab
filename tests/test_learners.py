import numpy as np
import pytest

from agents.learners.base import BaseLearner, OperantLearner
from agents.learners.rescorla_wagner import RescorlaWagnerLearner
from agents.learners.td_value import TDValueLearner
from agents.learners.q_learner import QLearner


class CoverageDummyLearner(BaseLearner):
    def update(self, state, reward, action=None, next_state=None, done=None):
        return None

    def value(self, state, action=None):
        return float(np.sum(state))


class CoverageDummyOperantLearner(OperantLearner):
    def update(self, state, reward, action=None, next_state=None, done=None):
        return None

    def value(self, state, action=None):
        return float(np.sum(state))


class CoverageBadLearner(BaseLearner):
    def update(self, state, reward, action=None, next_state=None, done=None):
        return super().update(state, reward, action, next_state, done)

    def value(self, state, action=None):
        return super().value(state, action)


def test_base_learner_hooks():
    learner = CoverageDummyLearner(alpha=0.1, gamma=0.9)
    state = np.asarray([1.0, 2.0])
    learner.update_with_alpha(state, 1.0)
    assert learner.value(state) == 3.0
    assert learner.expects_action() is False
    assert learner.start_episode() is None
    assert learner.end_episode() is None
    assert learner.get_parameters() == {}

    operant = CoverageDummyOperantLearner(alpha=0.1, gamma=0.9)
    assert operant.expects_action() is True

    bad = CoverageBadLearner(alpha=0.1, gamma=0.9)
    with pytest.raises(NotImplementedError):
        bad.update(state, 1.0)
    with pytest.raises(NotImplementedError):
        bad.value(state)


def test_rescorla_wagner_update_paths():
    learner = RescorlaWagnerLearner(state_dim=2, alpha=0.5)
    state = np.asarray([1.0, 0.0])
    learner.update(state, reward=1.0)
    assert learner.value(state) > 0

    salience = np.asarray([0.5, 0.5])
    learner2 = RescorlaWagnerLearner(state_dim=2, alpha=0.5, salience=salience)
    learner2.update(state, reward=1.0)
    assert learner2.value(state) > 0

    learner2.update_with_alpha(state, reward=1.0, alpha_override=0.1, delta_override=0.5)
    assert learner2.value(state) > 0


def test_td_value_update_paths():
    learner = TDValueLearner(state_dim=2, alpha=0.5, gamma=0.9)
    state = np.asarray([1.0, 0.0])
    next_state = np.asarray([0.5, 0.0])
    learner.update(state, reward=1.0, next_state=next_state, done=False)
    learner.update(state, reward=1.0, next_state=None, done=True)

    salience = np.asarray([0.5, 0.5])
    learner2 = TDValueLearner(state_dim=2, alpha=0.5, gamma=0.9, salience=salience)
    learner2.update(state, reward=1.0, next_state=next_state, done=False)
    learner2.update_with_alpha(state, reward=1.0, alpha_override=0.1, delta_override=0.2)


def test_qlearner_paths():
    learner = QLearner(state_dim=2, actions=[0, 1], alpha=0.5, gamma=0.9)
    state = np.asarray([1.0, 0.0])
    next_state = np.asarray([0.5, 0.0])

    assert learner.value(state) >= 0
    assert learner.value(state, action=0) >= 0

    with pytest.raises(ValueError):
        learner.update(state, reward=1.0, action=None, next_state=next_state)

    learner.update(state, reward=1.0, action=0, next_state=next_state, done=False)
    learner.update(state, reward=1.0, action=0, next_state=None, done=True)

    learner.salience = np.asarray([1.0, 1.0])
    learner.update(state, reward=1.0, action=0, next_state=next_state, done=False)

    learner.update_with_alpha(state, reward=1.0, action=None)
    learner.update_with_alpha(state, reward=1.0, action=1, alpha_override=0.1, delta_override=0.2)
    assert "weights" in learner.get_parameters()


def test_learner_salience_vector_does_not_reweight_updates():
    state = np.asarray([1.0, 0.0], dtype=float)

    base = RescorlaWagnerLearner(state_dim=2, alpha=0.5, salience=None)
    with_salience = RescorlaWagnerLearner(
        state_dim=2,
        alpha=0.5,
        salience=np.asarray([0.1, 1.0], dtype=float),
    )

    base.update(state, reward=1.0)
    with_salience.update(state, reward=1.0)

    np.testing.assert_allclose(base.weights, with_salience.weights)


class BaseDummyLearner(BaseLearner):
    def update(self, state, reward, action=None, next_state=None, done=None):
        self.last = (state, reward, action)

    def value(self, state, action=None):
        return 0.0


class BaseDummyOperant(OperantLearner):
    def update(self, state, reward, action=None, next_state=None, done=None):
        self.last = (state, reward, action)

    def value(self, state, action=None):
        return 0.0


def test_baselearner_update_with_alpha_calls_update():
    learner = BaseDummyLearner(alpha=0.1, gamma=0.0)
    learner.update_with_alpha(state=np.array([1.0]), reward=1.0, action=None)
    assert learner.last[1] == 1.0


def test_baselearner_expects_action_false():
    learner = BaseDummyLearner(alpha=0.1, gamma=0.0)
    assert learner.expects_action() is False


def test_baselearner_start_end_episode_noop():
    learner = BaseDummyLearner(alpha=0.1, gamma=0.0)
    assert learner.start_episode() is None
    assert learner.end_episode() is None


def test_baselearner_get_parameters_default():
    learner = BaseDummyLearner(alpha=0.1, gamma=0.0)
    assert learner.get_parameters() == {}


def test_operantlearner_expects_action_true():
    learner = BaseDummyOperant(alpha=0.1, gamma=0.9)
    assert learner.expects_action() is True


def test_qlearner_deterministic_update_fixture():
    learner = QLearner(state_dim=2, actions=["left", "right"], alpha=0.5, gamma=0.0)
    state = np.asarray([1.0, 0.0], dtype=float)

    learner.update(state, reward=1.0, action="left", next_state=None, done=True)
    # q <- 0 + 0.5*(1-0)*1 = 0.5
    assert learner.value(state, action="left") == pytest.approx(0.5, abs=1e-12)

    learner.update(state, reward=-1.0, action="left", next_state=None, done=True)
    # q <- 0.5 + 0.5*(-1-0.5)*1 = -0.25
    assert learner.value(state, action="left") == pytest.approx(-0.25, abs=1e-12)


def test_td_value_deterministic_update_fixture():
    learner = TDValueLearner(state_dim=2, alpha=0.5, gamma=0.5)
    state = np.asarray([1.0, 0.0], dtype=float)
    next_state = np.asarray([1.0, 0.0], dtype=float)

    learner.update(state, reward=1.0, next_state=next_state, done=False)
    # v0=0, v_next=0 => delta=1 => w0=0.5
    assert learner.value(state) == pytest.approx(0.5, abs=1e-12)

    learner.update(state, reward=0.0, next_state=next_state, done=False)
    # v=0.5, v_next=0.5 => delta=0.25-0.5=-0.25 => w0=0.375
    assert learner.value(state) == pytest.approx(0.375, abs=1e-12)
