from __future__ import annotations

from virtual_shaping_lab.vsl.agent import CompositionalAgent
from virtual_shaping_lab.vsl.contracts import Outcome, TaskInput
from virtual_shaping_lab.vsl.environment import CompiledProgramTestEnvironment
from virtual_shaping_lab.vsl.program import compile_environment_program
from virtual_shaping_lab.vsl.runtime import (
    build_runtime_learner_adapter,
    build_runtime_observation_adapter,
    build_runtime_policy_adapter,
)


def _build_runtime_stack():
    return (
        build_runtime_observation_adapter(preset_name="identity_observation"),
        build_runtime_learner_adapter(
            preset_name="rescorla_wagner",
            step_size=0.1,
            state={"weights": {"tone": 0.0}},
        ),
        build_runtime_policy_adapter(preset_name="no_policy"),
    )


def test_v3_20_15_environment_step_matches_compositional_agent_outputs_for_same_boundary_inputs():
    program = compile_environment_program(
        {
            "phases": [
                {
                    "name": "Acq",
                    "protocol": "acquisition",
                    "stimuli": {"cs_plus": ["tone"]},
                    "params": {"n_trials": 1, "outcome": 1.0},
                }
            ]
        }
    )
    obs_a, lrn_a, pol_a = _build_runtime_stack()
    env = CompiledProgramTestEnvironment(
        program,
        observation_adapter=obs_a,
        learner_adapter=lrn_a,
        policy_adapter=pol_a,
    )
    env.reset(seed=3)
    step = env.step(action=None)

    obs_b, lrn_b, pol_b = _build_runtime_stack()
    agent = CompositionalAgent(
        observation_adapter=obs_b,
        learner_adapter=lrn_b,
        policy_adapter=pol_b,
    )
    pre = agent.pre_outcome_step(
        TaskInput(
            stimuli=dict(step.stimulus),
            context=None,
            t=step.step_index,
            phase=step.protocol,
            available_actions=(),
        )
    )
    learner = agent.learn(
        observation=pre.observation_output,
        prediction=pre.prediction_output,
        action=pre.action.value,
        outcome=Outcome(
            reward=float(step.reward),
            next_stimuli={},
            terminated=bool(step.done),
            truncated=False,
        ),
    )
    assert step.metadata["observation"]["output"]["features"] == pre.observation_output.features
    assert step.metadata["learner"]["prediction"] == learner.prediction
    assert step.metadata["learner"]["error"] == learner.error
