from __future__ import annotations

from virtual_shaping_lab.vsl.agent import CompositionalAgent
from virtual_shaping_lab.vsl.agent.learning.bundle import LearnerStepResult
from virtual_shaping_lab.vsl.agent.learning.operators import PredictionOutput
from virtual_shaping_lab.vsl.agent.policy import PolicyOutput
from virtual_shaping_lab.vsl.contracts import Outcome, TaskInput
from virtual_shaping_lab.vsl.runtime import build_runtime_observation_adapter


def test_v3_20_15_compositional_agent_keeps_reward_outcome_out_of_policy_path():
    policy_calls: list[dict] = []
    learner_calls: list[dict] = []

    class _PolicyAdapter:
        def step(self, **kwargs):
            policy_calls.append(dict(kwargs))
            return PolicyOutput(
                action="leverpress",
                available_actions=("leverpress",),
                action_scores={"leverpress": 1.0},
                action_probabilities={"leverpress": 1.0},
                metadata={"variant": "policy_stub"},
            )

    class _LearnerAdapter:
        def step(self, **kwargs):
            learner_calls.append(dict(kwargs))
            return LearnerStepResult(
                prediction_output=PredictionOutput.from_state_value(0.0),
                prediction=0.0,
                next_prediction=0.0,
                error=float(kwargs.get("reward", 0.0)),
                done=bool(kwargs.get("done", False)),
                reward=float(kwargs.get("reward", 0.0)),
                features={"tone": 1.0},
                next_features=None,
                update_features={"tone": 1.0},
                state={},
                attention_state={},
                eligibility_state={},
                measurements={},
            )

    agent = CompositionalAgent(
        observation_adapter=build_runtime_observation_adapter(preset_name="identity_observation"),
        policy_adapter=_PolicyAdapter(),
        learner_adapter=_LearnerAdapter(),
    )
    pre = agent.pre_outcome_step(
        TaskInput(
            stimuli={"cs_plus": ["tone"]},
            context="A",
            t=0,
            phase="operant_conditioning",
            available_actions=("leverpress",),
        )
    )
    _ = agent.learn(
        observation=pre.observation_output,
        prediction=pre.prediction_output,
        action=pre.action.value,
        outcome=Outcome(reward=1.0, next_stimuli={}, terminated=True),
    )

    assert len(policy_calls) == 1
    assert "reward" not in policy_calls[0]
    assert "outcome" not in policy_calls[0]
    assert "prediction_error" not in policy_calls[0]

    assert len(learner_calls) == 1
    assert "reward" in learner_calls[0]
    assert "observation_features" in learner_calls[0]
    assert "stimulus" not in learner_calls[0]
