from __future__ import annotations

import pytest

from virtual_shaping_lab.vsl.environment import CompiledProgramTestEnvironment, RolloutHarness
from virtual_shaping_lab.vsl.program import compile_environment_program


def _compiled_fixture():
    payload = {
        "phases": [
            {
                "name": "Acq",
                "protocol": "acquisition",
                "stimuli": {"cs_plus": ["tone"]},
                "params": {"n_trials": 3, "outcome": 1.0},
            },
            {
                "name": "Ext",
                "protocol": "extinction",
                "stimuli": {"cs_plus": ["tone"]},
                "params": {"n_trials": 2, "outcome": 0.0},
            },
        ]
    }
    return compile_environment_program(payload)


def test_test_mode_rollout_harness_executes_environment_stepping():
    program = _compiled_fixture()
    env = CompiledProgramTestEnvironment(program)
    harness = RolloutHarness()

    records = harness.run(env, seed=11, action=None)
    assert len(records) == 5
    assert records[0]["protocol"] == "acquisition"
    assert records[-1]["protocol"] == "extinction"
    assert records[-1]["done"] is True


def test_test_mode_rollout_harness_is_deterministic_for_same_seed():
    program = _compiled_fixture()
    env_a = CompiledProgramTestEnvironment(program)
    env_b = CompiledProgramTestEnvironment(program)
    harness = RolloutHarness()

    rec_a = harness.run(env_a, seed=17, action=None)
    rec_b = harness.run(env_b, seed=17, action=None)
    assert rec_a == rec_b


def test_test_mode_rollout_harness_respects_max_steps():
    program = _compiled_fixture()
    env = CompiledProgramTestEnvironment(program)
    harness = RolloutHarness(max_steps=2)
    records = harness.run(env, seed=3)
    assert len(records) == 2
    assert records[-1]["done"] is False


def test_compiled_environment_raises_when_stepping_after_terminal():
    program = _compiled_fixture()
    env = CompiledProgramTestEnvironment(program)
    harness = RolloutHarness()
    _ = harness.run(env)
    with pytest.raises(StopIteration):
        env.step(action=None)
