from __future__ import annotations

import inspect

import numpy as np
import pytest
from jsonschema import ValidationError

from agents.operant_agent import OperantAgent
from agents.learners.q_learner import QLearner
from experiment.assemble import assemble_experiment
from experiment.config import ExperimentConfig
from experiment.phases.operant_acquisition import OperantAcquisitionPhase
from ui.validate_payload import validate_payload

from preset_payloads import operant_conditioning_payload, acquisition_payload


class _DummyRepresentation:
    def encode(self, observation):
        return np.asarray([1.0, 0.0], dtype=float)


class _SpyLearner:
    def __init__(self):
        self.calls = []

    def value(self, state, action=None):
        return float(np.sum(state))

    def update(self, state, reward, action=None):
        self.calls.append((state.copy(), float(reward), action))


class _ConstantPolicy:
    def __init__(self, action):
        self._action = action

    def select_action(self, state, value_fn=None):
        return self._action


def test_operant_agent_forwards_action_and_signed_reward_to_learner():
    learner = _SpyLearner()
    agent = OperantAgent(
        learner=learner,
        representation=_DummyRepresentation(),
        policy=_ConstantPolicy(action="left"),
    )
    state = agent.observe({"stimuli": ["lever"], "context": "A", "compound": False, "metadata": {}})
    assert agent.act(state) == "left"

    agent.update(state, reward=1.0, action="left")
    agent.update(state, reward=0.0, action="left")
    agent.update(state, reward=-1.0, action="left")

    rewards = [r for (_s, r, _a) in learner.calls]
    actions = [a for (_s, _r, a) in learner.calls]
    assert rewards == [1.0, 0.0, -1.0]
    assert actions == ["left", "left", "left"]


def test_qlearner_reward_sign_branches_update_direction():
    state = np.asarray([1.0, 0.0], dtype=float)

    pos = QLearner(state_dim=2, actions=["a0"], alpha=0.5, gamma=0.0)
    pos.update(state, reward=1.0, action="a0", next_state=None, done=True)
    assert pos.value(state, action="a0") > 0

    zero = QLearner(state_dim=2, actions=["a0"], alpha=0.5, gamma=0.0)
    zero.update(state, reward=0.0, action="a0", next_state=None, done=True)
    assert zero.value(state, action="a0") == pytest.approx(0.0, abs=1e-12)

    neg = QLearner(state_dim=2, actions=["a0"], alpha=0.5, gamma=0.0)
    neg.update(state, reward=-1.0, action="a0", next_state=None, done=True)
    assert neg.value(state, action="a0") < 0


def test_operant_phase_records_signed_rewards_and_actions():
    class _SequenceSchedule:
        name = "sequence"

        def __init__(self):
            self.rewards = [1.0, 0.0, -1.0]
            self.calls = []

        def reset(self):
            self.calls.clear()

        def step(self, action, t):
            self.calls.append((action, t))
            return self.rewards[t]

    class _Agent:
        def __init__(self):
            self._action = "action_0"
            self.representation = _DummyRepresentation()
            self.learner = type("L", (), {"attention_map": {}})()

        def observe(self, obs):
            return self.representation.encode(obs)

        def value(self, state):
            return 0.25

        def act(self, state):
            return self._action

        def update(self, state, reward, action=None):
            return None

    phase = OperantAcquisitionPhase(
        agent=_Agent(),
        stimuli={"cs_plus": ["lever"]},
        n_trials=3,
        reward_schedule=_SequenceSchedule(),
        params={},
    )

    records = []
    while True:
        rec = phase.step()
        if rec is None:
            break
        records.append(rec)

    assert [float(r["reward"]) for r in records] == [1.0, 0.0, -1.0]
    assert all(r["action"] == "action_0" for r in records)


def test_operant_payload_policy_guard_accepts_operant_and_rejects_classical():
    operant_payload = operant_conditioning_payload()
    validate_payload(operant_payload)

    classical_payload = acquisition_payload()
    classical_payload["experiment"]["policy"] = {
        "name": "epsilon_greedy",
        "params": {"actions": ["action_0", "action_1"], "epsilon": 0.1},
    }
    with pytest.raises(ValidationError):
        validate_payload(classical_payload)


def test_operant_fixture_assembles_operant_agent_and_action_learner():
    payload = operant_conditioning_payload()
    cfg = ExperimentConfig.from_payload(payload)
    runtime_units, agent, _rep = assemble_experiment(cfg)
    assert runtime_units
    assert agent.__class__.__name__ == "OperantAgent"
    assert agent.learner.__class__.__name__ == "QLearner"
    assert agent.learner.expects_action() is True


@pytest.mark.xfail(reason="v1.4 contract target: operant agent should require policy/action path")
def test_operant_agent_should_not_allow_none_action_path():
    agent = OperantAgent(
        learner=_SpyLearner(),
        representation=_DummyRepresentation(),
        policy=None,
    )
    action = agent.act(np.asarray([1.0, 0.0], dtype=float))
    assert action is not None


@pytest.mark.xfail(reason="v1.4 contract target: agent update signature should support next_state/done")
def test_operant_agent_update_signature_should_accept_next_state_and_done():
    sig = inspect.signature(OperantAgent.update)
    assert "next_state" in sig.parameters
    assert "done" in sig.parameters
