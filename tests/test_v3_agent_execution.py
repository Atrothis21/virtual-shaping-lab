from __future__ import annotations

from virtual_shaping_lab.vsl.agent import AgentStepResult, CompositionalAgent
from virtual_shaping_lab.vsl.contracts import Outcome, TaskInput
from virtual_shaping_lab.vsl.runtime import (
    build_runtime_learner_adapter,
    build_runtime_observation_adapter,
    build_runtime_policy_adapter,
)


def _build_agent() -> CompositionalAgent:
    return CompositionalAgent(
        observation_adapter=build_runtime_observation_adapter(preset_name="identity_observation"),
        learner_adapter=build_runtime_learner_adapter(
            preset_name="rescorla_wagner",
            step_size=0.1,
            state={"weights": {"tone": 0.0}},
        ),
        policy_adapter=build_runtime_policy_adapter(preset_name="uniform_random"),
    )


def test_v3_20_15_compositional_agent_pre_outcome_step_contract():
    agent = _build_agent()
    out = agent.pre_outcome_step(
        TaskInput(
            stimuli={"cs_plus": ["tone"]},
            context="A",
            t=0,
            phase="operant_conditioning",
            available_actions=("left", "right"),
        )
    )
    assert isinstance(out, AgentStepResult)
    assert out.metadata["pipeline_order"] == ["observe", "predict", "act"]
    assert isinstance(out.observation_output.features, list)
    assert out.action.value in {"left", "right"}


def test_v3_20_15_compositional_agent_post_outcome_learning_contract():
    agent = _build_agent()
    pre = agent.pre_outcome_step(
        TaskInput(
            stimuli={"cs_plus": ["tone"]},
            context="A",
            t=0,
            phase="operant_conditioning",
            available_actions=("left", "right"),
        )
    )
    learner = agent.learn(
        observation=pre.observation_output,
        prediction=pre.prediction_output,
        action=pre.action.value,
        outcome=Outcome(reward=1.0, terminated=True, next_stimuli={}),
    )
    assert learner.reward == 1.0
    assert isinstance(learner.error, float)
    t = agent.advance_internal_time(1.0)
    assert t == 1.0
