import numpy as np
import pytest

from agents.composed_agent import ComposedAgent
from agents.learners.rescorla_wagner import RescorlaWagnerLearner
from agents.policies.epsilon_greedy import EpsilonGreedyPolicy
from agents.policies.null_policy import NullPolicy
from agents.policies.softmax import SoftmaxPolicy
from agents.representations.observation import make_observation
from agents.representations.vector_elemental import VectorElementalRepresentation
from domain.types import EncodedState, Observation, Transition


class DummyRepresentation:
    def __init__(self):
        self.reset_called = False

    def encode(self, observation: Observation) -> EncodedState:
        return EncodedState(x=np.asarray([1.0, 2.0], dtype=float), key="dummy")

    @property
    def dimension(self) -> int:
        return 2

    def reset(self):
        self.reset_called = True


class DummyLearner:
    def __init__(self):
        self.reset_called = False
        self.last_transition = None

    def reset(self):
        self.reset_called = True

    def value(self, state: EncodedState, action=None):
        return float(np.sum(state.x))

    def update(self, transition: Transition):
        self.last_transition = transition


class DummyPolicy:
    def __init__(self):
        self.reset_called = False

    def reset(self):
        self.reset_called = True

    def select_action(self, state, actions, value_fn, rng):
        return actions[0] if actions else None


def test_composed_agent_observe_value_learn_paths():
    learner = DummyLearner()
    rep = DummyRepresentation()
    agent = ComposedAgent(learner=learner, representation=rep, policy=NullPolicy())

    state = agent.observe(Observation(stimuli=["tone"], context="A"))
    assert state.key == "dummy"
    assert agent.value(state) == 3.0

    tr = Transition(s=state, r=1.0)
    agent.learn(tr)
    assert learner.last_transition is tr
    assert agent.act(state, actions=["press"], rng=np.random.default_rng(1)) is None


def test_composed_agent_operant_action_selection():
    learner = RescorlaWagnerLearner(state_dim=2, alpha=0.1)
    rep = DummyRepresentation()
    policy = EpsilonGreedyPolicy(epsilon=0.0)
    agent = ComposedAgent(learner=learner, representation=rep, policy=policy)

    state = agent.observe(Observation(stimuli=["tone"], context="A"))
    action = agent.act(state, actions=["left", "right"], rng=np.random.default_rng(7))
    assert action in {"left", "right"}


def test_composed_agent_reset_delegates():
    learner = DummyLearner()
    rep = DummyRepresentation()
    policy = DummyPolicy()
    agent = ComposedAgent(learner=learner, representation=rep, policy=policy)

    agent.reset()
    assert learner.reset_called is True
    assert rep.reset_called is True
    assert policy.reset_called is True


def test_composed_agent_exposes_policy_distribution():
    learner = RescorlaWagnerLearner(state_dim=2, alpha=0.1)
    rep = DummyRepresentation()
    policy = EpsilonGreedyPolicy(epsilon=0.2)
    agent = ComposedAgent(learner=learner, representation=rep, policy=policy)

    state = agent.observe(Observation(stimuli=["tone"], context="A"))
    distribution = agent.policy_distribution(state, actions=["left", "right"])

    assert distribution is not None
    assert set(distribution.keys()) == {"left", "right"}
    assert distribution["left"] == pytest.approx(0.9)
    assert distribution["right"] == pytest.approx(0.1)
    assert sum(distribution.values()) == pytest.approx(1.0)


def test_softmax_policy_distribution_is_normalized():
    policy = SoftmaxPolicy(temperature=1.0)
    state = EncodedState(x=np.asarray([1.0, 2.0], dtype=float))

    def value_fn(_state, action):
        return {"left": 1.0, "right": 2.0}[action]

    distribution = policy.action_distribution(state, ["left", "right"], value_fn)

    assert distribution["right"] > distribution["left"]
    assert sum(distribution.values()) == pytest.approx(1.0)


def test_null_policy_distribution_exposes_zero_mass():
    state = EncodedState(x=np.asarray([1.0], dtype=float))
    distribution = NullPolicy().action_distribution(state, ["press"], lambda *_args, **_kwargs: 0.0)
    assert distribution == {"press": 0.0}


def test_uniform_static_attention_matches_none_attention_baseline():
    state = EncodedState(x=np.asarray([1.0, 0.0], dtype=float))
    transition = Transition(s=state, r=1.0, metadata={"cue_labels": ["tone"]})

    none_attention = RescorlaWagnerLearner(state_dim=2, alpha=0.5)
    uniform_attention = RescorlaWagnerLearner(state_dim=2, alpha=0.5)
    uniform_attention.set_attention_config(
        name="static",
        params={"default": 1.0, "overrides": {"tone": 1.0}},
    )

    none_attention.update(transition)
    uniform_attention.update(transition)

    np.testing.assert_allclose(none_attention.weights, uniform_attention.weights)


def test_composed_agent_normalizes_raw_state_vectors():
    learner = DummyLearner()
    rep = DummyRepresentation()
    agent = ComposedAgent(learner=learner, representation=rep, policy=DummyPolicy())

    raw = np.asarray([1.0, 2.0], dtype=float)
    assert agent.value(raw) == 3.0

    tr = Transition(s=EncodedState(x=raw), r=0.5, a="a")
    agent.learn(tr)
    assert learner.last_transition.a == "a"


def test_context_and_similarity_interaction_stays_context_local():
    rep = VectorElementalRepresentation(
        params={
            "stimuli": ["tone", "noise"],
            "contexts": ["A", "B"],
            "include_global": False,
            "include_context": True,
            "similarity": {
                "type": "matrix",
                "stimuli": ["tone", "noise"],
                "values": [
                    [1.0, 0.4],
                    [0.4, 1.0],
                ],
            },
        }
    )

    vec = rep.encode(make_observation(["tone"], "A")).x

    idx_a_tone = rep._encoder._index["ctx:A|tone"]
    idx_a_noise = rep._encoder._index["ctx:A|noise"]
    idx_b_tone = rep._encoder._index["ctx:B|tone"]
    idx_b_noise = rep._encoder._index["ctx:B|noise"]

    assert vec[idx_a_tone] == pytest.approx(1.0)
    assert vec[idx_a_noise] == pytest.approx(0.4)
    assert vec[idx_b_tone] == pytest.approx(0.0)
    assert vec[idx_b_noise] == pytest.approx(0.0)


def test_salience_and_attention_interaction_compose_multiplicatively():
    rep = VectorElementalRepresentation(
        params={
            "stimuli": ["tone"],
            "include_global": True,
            "include_context": False,
            "salience": {"tone": 0.5},
        }
    )
    learner = RescorlaWagnerLearner(state_dim=rep.dimension, alpha=1.0)
    learner.set_attention_config(
        name="static",
        params={"default": 0.5, "overrides": {"tone": 0.5}},
    )
    agent = ComposedAgent(learner=learner, representation=rep, policy=NullPolicy())

    state = agent.observe(make_observation(["tone"], "A"))
    agent.learn(
        Transition(
            s=state,
            r=1.0,
            metadata={"cue_labels": ["tone"]},
        )
    )

    assert learner.weights[0] == pytest.approx(0.25)
