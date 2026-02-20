import numpy as np
import pytest

from agents.base import Agent
from agents.classical_agent import ClassicalAgent
from agents.operant_agent import OperantAgent


class CoverageDummyRepresentation:
    def __init__(self):
        self.reset_called = False

    def encode(self, observation):
        return np.asarray([1.0, 2.0])

    def reset(self):
        self.reset_called = True


class CoverageDummyLearner:
    def __init__(self):
        self.updated = False
        self.reset_called = False

    def value(self, state, action=None):
        return float(np.sum(state))

    def update(self, state, reward, action=None):
        self.updated = True

    def reset(self):
        self.reset_called = True


class CoverageDummyPolicy:
    def __init__(self, mode="value"):
        self.mode = mode
        self.reset_called = False

    def reset(self):
        self.reset_called = True

    def select_action(self, state, value_fn=None):
        if self.mode == "value":
            return 1 if value_fn else 0
        return 0


class CoverageDummyPolicyNoValue:
    def select_action(self, state):
        return 0


def test_classical_agent_paths():
    agent = ClassicalAgent(learner=CoverageDummyLearner(), representation=CoverageDummyRepresentation())
    state = agent.observe({"stimuli": ["tone"], "context": "A", "compound": False, "metadata": {}})
    assert state.shape == (2,)
    assert agent.value(state) == 3.0
    agent.update(state, reward=1.0, action=None)
    assert agent.act(state) is None

    agent.reset()
    assert agent.learner.reset_called is True
    assert agent.representation.reset_called is True


def test_classical_agent_missing_update():
    class NoUpdateLearner:
        def value(self, state, action=None):
            return 0.0

    agent = ClassicalAgent(learner=NoUpdateLearner(), representation=CoverageDummyRepresentation())
    with pytest.raises(AttributeError):
        agent.update(np.asarray([1.0, 2.0]), reward=1.0)


def test_operant_agent_paths():
    agent = OperantAgent(
        learner=CoverageDummyLearner(),
        representation=CoverageDummyRepresentation(),
        policy=CoverageDummyPolicy(mode="value"),
    )
    state = agent.observe({"stimuli": ["tone"], "context": "A", "compound": False, "metadata": {}})
    assert agent.value(state) == 3.0
    agent.update(state, reward=1.0, action=1)
    assert agent.act(state) == 1

    agent.reset()
    assert agent.learner.reset_called is True
    assert agent.representation.reset_called is True
    assert agent.policy.reset_called is True


def test_operant_agent_policy_fallbacks():
    agent = OperantAgent(
        learner=CoverageDummyLearner(),
        representation=CoverageDummyRepresentation(),
        policy=None,
    )
    assert agent.act(np.asarray([1.0, 2.0])) is None

    agent2 = OperantAgent(
        learner=CoverageDummyLearner(),
        representation=CoverageDummyRepresentation(),
        policy=CoverageDummyPolicyNoValue(),
    )
    assert agent2.act(np.asarray([1.0, 2.0])) == 0


def test_operant_agent_missing_update():
    class NoUpdateLearner:
        def value(self, state, action=None):
            return 0.0

    agent = OperantAgent(
        learner=NoUpdateLearner(),
        representation=CoverageDummyRepresentation(),
        policy=CoverageDummyPolicy(),
    )
    with pytest.raises(AttributeError):
        agent.update(np.asarray([1.0, 2.0]), reward=1.0, action=0)


class BaseDummyLearner:
    def __init__(self):
        self.calls = []

    def update_with_alpha(self, *args, **kwargs):
        self.calls.append((args, kwargs))


class BasePolicyWithValue:
    def select_action(self, state, value_fn=None):
        return 1 if value_fn else 0


class BasePolicyNoValue:
    def select_action(self, state):
        return 0


class BaseDummyAgent(Agent):
    def __init__(self):
        self.learner = BaseDummyLearner()
        self.policy = None

    def reset(self) -> None:
        return super().reset()

    def observe(self, observation):
        return super().observe(observation)

    def update(self, state, reward, action=None):
        return super().update(state, reward, action)

    def value(self, state, action=None):
        return super().value(state, action)


def test_agent_base_abstract_methods_and_act():
    agent = BaseDummyAgent()
    assert agent.reset() is None
    assert agent.observe({"stimuli": ["tone"], "context": "A", "compound": False, "metadata": {}}) is None
    assert agent.update(np.asarray([1.0, 2.0]), reward=1.0, action=None) is None
    assert agent.value(np.asarray([1.0, 2.0])) is None

    assert agent.act(np.asarray([1.0, 2.0])) is None

    agent.policy = BasePolicyWithValue()
    assert agent.act(np.asarray([1.0, 2.0])) == 1

    agent.policy = BasePolicyNoValue()
    assert agent.act(np.asarray([1.0, 2.0])) == 0

    agent.policy = object()
    assert agent.act(np.asarray([1.0, 2.0])) is None


def test_agent_update_with_alpha_paths():
    class NoAlphaLearner:
        pass

    agent = BaseDummyAgent()
    agent.update = lambda *args, **kwargs: "fallback"
    agent.update_with_alpha(np.asarray([1.0]), reward=1.0)
    assert agent.learner.calls

    agent.learner = NoAlphaLearner()
    agent.update_with_alpha(np.asarray([1.0]), reward=1.0, action=None, alpha_override=0.1, delta_override=0.2)


class LegacyDummyPolicyWithValue:
    def select_action(self, state, value_fn):
        return 1


class LegacyDummyPolicyStateOnly:
    def select_action(self, state):
        return 0


class LegacyDummyLearner:
    def __init__(self):
        self.last = None

    def update_with_alpha(self, state, reward, action=None, alpha_override=None, delta_override=None):
        self.last = ("alpha", state, reward, action, alpha_override, delta_override)


class LegacyDummyAgent(Agent):
    def __init__(self):
        self.policy = None
        self.learner = None
        self.updated = None

    def reset(self) -> None:
        self.updated = "reset"

    def observe(self, observation):
        return np.array([1.0])

    def update(self, state, reward, action=None) -> None:
        self.updated = ("update", state, reward, action)

    def value(self, state, action=None) -> float:
        return 0.5


def test_act_no_policy():
    agent = LegacyDummyAgent()
    assert agent.act(np.array([1.0])) is None


def test_act_policy_with_value_fn():
    agent = LegacyDummyAgent()
    agent.policy = LegacyDummyPolicyWithValue()
    assert agent.act(np.array([1.0])) == 1


def test_act_policy_state_only():
    agent = LegacyDummyAgent()
    agent.policy = LegacyDummyPolicyStateOnly()
    assert agent.act(np.array([1.0])) == 0


def test_act_policy_without_select_action():
    agent = LegacyDummyAgent()
    agent.policy = object()
    assert agent.act(np.array([1.0])) is None


def test_update_with_alpha_uses_learner():
    agent = LegacyDummyAgent()
    agent.learner = LegacyDummyLearner()
    agent.update_with_alpha(np.array([1.0]), reward=1.0, action=None, alpha_override=0.3)
    assert agent.learner.last[0] == "alpha"


def test_update_with_alpha_falls_back_to_update():
    agent = LegacyDummyAgent()
    agent.learner = object()
    agent.update_with_alpha(np.array([1.0]), reward=1.0, action=None)
    assert agent.updated[0] == "update"
