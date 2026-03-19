from __future__ import annotations

from experiment.runner import Runner
from virtual_shaping_lab.vsl.environment import CompiledProgramTestEnvironment
from virtual_shaping_lab.vsl.program import compile_environment_program


def _compiled_classical_env() -> CompiledProgramTestEnvironment:
    program = compile_environment_program(
        {
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
    )
    return CompiledProgramTestEnvironment(program)


def test_runner_executes_environment_contract_end_to_end():
    records = Runner(_compiled_classical_env(), seed=11).run()
    assert len(records) == 5
    assert records[0]["phase_name"] == "acquisition"
    assert records[-1]["phase_name"] == "extinction"
    assert records[-1]["done"] is True


def test_runner_environment_path_emits_trial_state_metadata():
    records = Runner(_compiled_classical_env(), seed=3).run()
    assert records
    for rec in records:
        ts = rec["metadata"]["trial_state"]
        assert isinstance(ts, dict)
        assert set(("s", "x", "z", "w", "a", "u", "y", "m")).issubset(ts.keys())


def test_runner_environment_replay_is_hash_identical_for_10_of_10_runs():
    streams = [Runner(_compiled_classical_env(), seed=17).run() for _ in range(10)]
    baseline = streams[0]
    assert all(stream == baseline for stream in streams[1:])
