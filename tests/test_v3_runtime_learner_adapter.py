from __future__ import annotations

from virtual_shaping_lab.vsl.environment import CompiledProgramTestEnvironment, RolloutHarness
from virtual_shaping_lab.vsl.program import compile_environment_program
from virtual_shaping_lab.vsl.runtime import RuntimeLearnerAdapter, build_runtime_learner_adapter


def test_v3_18_10_runtime_learner_adapter_steps_through_canonical_bundle():
    adapter = build_runtime_learner_adapter(
        preset_name="rescorla_wagner",
        step_size=0.1,
        state={"weights": {"tone": 0.0}},
    )
    assert isinstance(adapter, RuntimeLearnerAdapter)
    out = adapter.step(
        stimulus={"cs_plus": ["tone"]},
        next_stimulus={"cs_plus": ["tone"]},
        reward=1.0,
        done=False,
    )
    assert out.prediction == 0.0
    assert out.error == 1.0
    assert out.update_features["tone"] > 0.0


def test_v3_18_10_compiled_environment_routes_learner_execution_through_adapter():
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
    env = CompiledProgramTestEnvironment(
        program,
        learner_adapter=build_runtime_learner_adapter(
            preset_name="rescorla_wagner",
            step_size=0.1,
            state={"weights": {"tone": 0.0}},
        ),
    )
    records = RolloutHarness().run(env, seed=7)
    assert records
    for rec in records:
        learner = rec["metadata"]["learner"]
        ts = rec["trial_state"]
        assert isinstance(learner, dict)
        assert "prediction" in learner
        assert "error" in learner
        assert learner["prediction"] == ts["m"]["derived"]["prediction"]
        assert learner["error"] == ts["m"]["derived"]["error"]

