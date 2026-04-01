from __future__ import annotations

import pytest

from virtual_shaping_lab.vsl.agent import AgentStepResult, CompositionalAgent
from virtual_shaping_lab.vsl.contracts import TaskInput


def test_v3_20_15_compositional_agent_public_methods_exist_and_are_callable():
    agent = CompositionalAgent()
    assert callable(agent.observe)
    assert callable(agent.predict)
    assert callable(agent.act)
    assert callable(agent.learn)
    assert callable(agent.advance_internal_time)
    assert callable(agent.pre_outcome_step)


def test_v3_20_15_compositional_agent_observe_accepts_typed_or_mapping_task_input():
    agent = CompositionalAgent()
    out_a = agent.observe(TaskInput(stimuli={"cs_plus": ["tone"]}, context="A"))
    out_b = agent.observe({"stimuli": {"cs_plus": ["tone"]}, "context": "A"})
    assert out_a.output.feature_names
    assert out_b.output.feature_names


def test_v3_20_15_compositional_agent_pre_outcome_returns_typed_step_result():
    agent = CompositionalAgent()
    step = agent.pre_outcome_step(
        TaskInput(
            stimuli={"cs_plus": ["tone"]},
            context="A",
            available_actions=("left", "right"),
        )
    )
    assert isinstance(step, AgentStepResult)


def test_v3_20_15_compositional_agent_predict_requires_observation_when_no_prior_observe():
    agent = CompositionalAgent()
    with pytest.raises(ValueError, match="No observation available"):
        agent.predict()
