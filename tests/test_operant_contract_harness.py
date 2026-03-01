from __future__ import annotations

import numpy as np
import pytest
from jsonschema import ValidationError

from agents.composed_agent import ComposedAgent
from agents.learners.q_learner import QLearner
from experiment.assemble import assemble_experiment
from experiment.config import ExperimentConfig
from experiment.domain.types import TrialTimeSpec
from experiment.phases.operant_acquisition import OperantAcquisitionPhase
from ui.validate_payload import validate_payload

from domain.types import EncodedState, Observation, Transition
from preset_payloads import acquisition_payload, operant_conditioning_payload


class _DummyRepresentation:
    def reset(self):
        return None

    def encode(self, observation):
        return EncodedState(x=np.asarray([1.0, 0.0], dtype=float))


class _SpyLearner:
    def __init__(self):
        self.calls = []

    def reset(self):
        return None

    def value(self, state, action=None):
        return float(np.sum(state.x))

    def update(self, transition: Transition):
        self.calls.append(transition)


class _ConstantPolicy:
    def __init__(self, action):
        self._action = action

    def reset(self):
        return None

    def select_action(self, state, actions, value_fn, rng):
        if self._action is not None:
            return self._action
        return actions[0] if actions else None


def test_operant_agent_forwards_action_and_signed_reward_to_learner():
    learner = _SpyLearner()
    agent = ComposedAgent(
        learner=learner,
        representation=_DummyRepresentation(),
        policy=_ConstantPolicy(action="left"),
    )
    state = agent.observe(Observation(stimuli=["lever"], context="A"))
    assert agent.act(state, actions=["left"]) == "left"

    agent.learn(Transition(s=state, r=1.0, a="left", done=True))
    agent.learn(Transition(s=state, r=0.0, a="left", done=True))
    agent.learn(Transition(s=state, r=-1.0, a="left", done=True))

    rewards = [tr.r for tr in learner.calls]
    actions = [tr.a for tr in learner.calls]
    assert rewards == [1.0, 0.0, -1.0]
    assert actions == ["left", "left", "left"]


def test_qlearner_reward_sign_branches_update_direction():
    state = EncodedState(x=np.asarray([1.0, 0.0], dtype=float))

    pos = QLearner(state_dim=2, actions=["a0"], alpha=0.5, gamma=0.0)
    pos.update(Transition(s=state, r=1.0, a="a0", s_next=None, done=True))
    assert pos.value(state, action="a0") > 0

    zero = QLearner(state_dim=2, actions=["a0"], alpha=0.5, gamma=0.0)
    zero.update(Transition(s=state, r=0.0, a="a0", s_next=None, done=True))
    assert zero.value(state, action="a0") == pytest.approx(0.0, abs=1e-12)

    neg = QLearner(state_dim=2, actions=["a0"], alpha=0.5, gamma=0.0)
    neg.update(Transition(s=state, r=-1.0, a="a0", s_next=None, done=True))
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

        def act(self, state, actions=None, rng=None):
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


def test_operant_payload_requires_policy_at_validation():
    payload = operant_conditioning_payload()
    payload["experiment"].pop("policy", None)
    with pytest.raises(ValidationError, match="operant experiments require a policy object"):
        validate_payload(payload)


def test_operant_fixture_assembles_composed_agent_and_action_learner():
    payload = operant_conditioning_payload()
    cfg = ExperimentConfig.from_payload(payload)
    runtime_units, agent, _rep = assemble_experiment(cfg)
    assert runtime_units
    assert agent.__class__.__name__ == "ComposedAgent"
    assert agent.learner.__class__.__name__ == "QLearner"
    assert agent.learner.expects_action() is True


def test_operant_agent_none_policy_uses_null_behavior():
    agent = ComposedAgent(
        learner=_SpyLearner(),
        representation=_DummyRepresentation(),
        policy=None,
    )
    state = agent.observe(Observation(stimuli=["lever"], context="A"))
    assert agent.act(state, actions=["left"]) is None


def test_composed_agent_learn_forwards_next_state_and_done_to_learner():
    learner = _SpyLearner()
    agent = ComposedAgent(
        learner=learner,
        representation=_DummyRepresentation(),
        policy=_ConstantPolicy(action="left"),
    )
    state = EncodedState(x=np.asarray([1.0, 0.0], dtype=float))
    next_state = EncodedState(x=np.asarray([0.5, 0.0], dtype=float))
    agent.learn(Transition(s=state, r=0.25, a="left", s_next=next_state, done=False))

    assert len(learner.calls) == 1
    tr = learner.calls[0]
    assert tr.r == pytest.approx(0.25, abs=1e-12)
    assert tr.a == "left"
    assert tr.s_next is not None
    np.testing.assert_allclose(tr.s_next.x, next_state.x)
    assert tr.done is False


def test_operant_phase_build_trial_schedule_attaches_schedule_runtime():
    class _Schedule:
        name = "fixed_ratio"

        def reset(self):
            return None

        def step(self, action, t):
            return 0.0

        def build_tick_runtime(self, time_spec):
            return object()

    class _Agent:
        def __init__(self):
            self.representation = _DummyRepresentation()
            self.learner = type("L", (), {"attention_map": {}})()
            self.policy = type("P", (), {"actions": ["press"]})()

        def reset(self):
            return None

        def observe(self, obs):
            return self.representation.encode(obs)

        def value(self, state):
            return 0.0

        def act(self, state, actions=None, rng=None):
            return "press"

    phase = OperantAcquisitionPhase(
        agent=_Agent(),
        stimuli={"cs_plus": ["lever"]},
        n_trials=1,
        reward_schedule=_Schedule(),
        params={"trial_time_spec": TrialTimeSpec(duration_s=1.0, dt_s=0.25)},
    )
    schedule = phase.build_trial_schedule(ctx=None, trial_index=0)
    assert schedule is not None
    assert "schedule_runtime" in schedule.metadata
