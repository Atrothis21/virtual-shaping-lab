from __future__ import annotations

import inspect

from virtual_shaping_lab.vsl.environment import CompiledProgramTestEnvironment, RolloutHarness
from virtual_shaping_lab.vsl.program import compile_environment_program
from virtual_shaping_lab.vsl.runtime.learner_adapter import RuntimeLearnerAdapter


def test_v3_19_15_runtime_learner_adapter_is_observation_feature_only():
    params = inspect.signature(RuntimeLearnerAdapter.step).parameters
    assert "observation_features" in params
    assert "observation_feature_names" in params
    assert "next_observation_features" in params
    assert "next_observation_feature_names" in params
    assert "stimulus" not in params
    assert "next_stimulus" not in params


def test_v3_19_15_environment_runtime_emits_single_path_observation_and_learner_feature_contract():
    program = compile_environment_program(
        {
            "phases": [
                {
                    "name": "Acq",
                    "protocol": "acquisition",
                    "stimuli": {"cs_plus": ["tone"]},
                    "params": {"n_trials": 2, "outcome": 1.0},
                }
            ]
        }
    )
    env = CompiledProgramTestEnvironment(program)
    records = RolloutHarness().run(env, seed=3)

    assert records
    for rec in records:
        metadata = rec["metadata"]
        learner = metadata["learner"]
        observation = metadata["observation"]["output"]
        assert isinstance(observation.get("metadata", {}).get("stage_traces"), dict)
        assert learner["input_features"] == {
            name: value
            for name, value in zip(
                observation["feature_names"],
                observation["features"],
            )
        }
