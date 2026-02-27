import numpy as np
import pytest

from agents.composed_agent import ComposedAgent
from agents.interfaces import ILearner, IPolicy, IRepresentation
from agents.learners.q_learner import QLearner
from agents.learners.rescorla_wagner import RescorlaWagnerLearner
from agents.policies.epsilon_greedy import EpsilonGreedyPolicy
from agents.policies.null_policy import NullPolicy
from agents.representations.observation import make_observation
from agents.representations.vector_elemental import VectorElementalRepresentation
from domain.types import EncodedState, Observation, Transition


class PlugRepresentation(IRepresentation):
    def reset(self) -> None:
        return None

    def encode(self, observation: Observation) -> EncodedState:
        return EncodedState(x=np.array([1.0, 0.0], dtype=float), key="plug")


class PlugLearner(ILearner):
    def __init__(self):
        self.last_transition = None

    def reset(self) -> None:
        self.last_transition = None

    def value(self, state: EncodedState, action=None) -> float:
        return float(np.sum(state.x))

    def update(self, transition: Transition) -> None:
        self.last_transition = transition


class PlugPolicy(IPolicy):
    def reset(self) -> None:
        return None

    def select_action(self, state: EncodedState, actions, value_fn, rng):
        return actions[0] if actions else None


class CaptureLearner(ILearner):
    def __init__(self):
        self.last_transition = None

    def reset(self) -> None:
        self.last_transition = None

    def value(self, state: EncodedState, action=None) -> float:
        return 0.0

    def update(self, transition: Transition) -> None:
        self.last_transition = transition


class PassThroughRepresentation(IRepresentation):
    def reset(self) -> None:
        return None

    def encode(self, observation: Observation) -> EncodedState:
        return EncodedState(x=np.array([1.0], dtype=float), key="time")


def test_classical_flow_with_null_policy() -> None:
    rep = VectorElementalRepresentation({"stimuli": ["tone"]})
    learner = RescorlaWagnerLearner(state_dim=rep.dimension, alpha=0.5)
    agent = ComposedAgent(learner=learner, representation=rep, policy=NullPolicy())

    obs = make_observation(["tone"], context="A")
    state = agent.observe(obs)
    assert agent.act(state, actions=["press"], rng=np.random.default_rng(1)) is None

    agent.learn(Transition(s=state, r=1.0))
    assert agent.value(state) > 0.0


def test_operant_policy_is_deterministic_with_seeded_rng() -> None:
    rep = VectorElementalRepresentation({"stimuli": ["lever"]})

    agent_1 = ComposedAgent(
        learner=QLearner(state_dim=rep.dimension, actions=["left", "right"]),
        representation=rep,
        policy=EpsilonGreedyPolicy(epsilon=1.0),
    )
    agent_2 = ComposedAgent(
        learner=QLearner(state_dim=rep.dimension, actions=["left", "right"]),
        representation=rep,
        policy=EpsilonGreedyPolicy(epsilon=1.0),
    )

    state_1 = agent_1.observe(make_observation(["lever"], context="A"))
    state_2 = agent_2.observe(make_observation(["lever"], context="A"))

    rng_a = np.random.default_rng(1234)
    rng_b = np.random.default_rng(1234)

    sequence_1 = [agent_1.act(state_1, actions=["left", "right"], rng=rng_a) for _ in range(5)]
    sequence_2 = [agent_2.act(state_2, actions=["left", "right"], rng=rng_b) for _ in range(5)]

    assert sequence_1 == sequence_2


def test_composed_agent_is_pluggable_with_new_components() -> None:
    learner = PlugLearner()
    rep = PlugRepresentation()
    policy = PlugPolicy()
    agent = ComposedAgent(learner=learner, representation=rep, policy=policy)

    state = agent.observe(Observation(stimuli=["x"], context="A"))
    action = agent.act(state, actions=["a", "b"], rng=np.random.default_rng(7))
    agent.learn(Transition(s=state, r=0.5, a=action, done=False))

    assert state.key == "plug"
    assert action == "a"
    assert learner.last_transition is not None
    assert learner.last_transition.a == "a"


def test_transition_time_fields_passthrough_to_learner() -> None:
    learner = CaptureLearner()
    rep = PassThroughRepresentation()
    agent = ComposedAgent(learner=learner, representation=rep, policy=NullPolicy())

    state = agent.observe(Observation(stimuli=["cue"], context="A", t_s=3.0, dt_s=0.5))
    transition = Transition(s=state, r=0.25, t_s=3.0, dt_s=0.5)
    agent.learn(transition)

    assert learner.last_transition is not None
    assert learner.last_transition.t_s == 3.0
    assert learner.last_transition.dt_s == 0.5


def test_mechanism_split_representation_vs_learner_attention() -> None:
    rep = VectorElementalRepresentation(
        {
            "stimuli": ["tone", "noise"],
            "contexts": ["A"],
            "salience": {"tone": 0.5, "noise": 0.5},
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
    learner = RescorlaWagnerLearner(state_dim=rep.dimension, alpha=1.0)
    learner.set_attention_map({"tone": 0.2})
    agent = ComposedAgent(learner=learner, representation=rep, policy=NullPolicy())

    obs = Observation(stimuli=["tone"], context="A")
    state = agent.observe(obs)
    before = learner.weights.copy()
    agent.learn(Transition(s=state, r=1.0, metadata={"cue_labels": ["tone"]}))
    delta = learner.weights - before

    idx_tone = rep._encoder._index["global:tone"]
    idx_noise = rep._encoder._index["global:noise"]
    # Representation side: similarity + salience already applied in state.x.
    assert state.x[idx_tone] == 0.5
    assert state.x[idx_noise] == 0.2
    # Learner side: attention scales update magnitude (alpha_eff = 1.0 * 0.2).
    assert delta[idx_tone] == pytest.approx(0.1)
    assert delta[idx_noise] == pytest.approx(0.04)
