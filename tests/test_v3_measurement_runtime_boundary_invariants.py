from __future__ import annotations

from copy import deepcopy
from pathlib import Path

from virtual_shaping_lab.vsl.environment import CompiledProgramTestEnvironment
from virtual_shaping_lab.vsl.program import compile_environment_program
from virtual_shaping_lab.vsl.rollout import ReplayHarness
from virtual_shaping_lab.vsl.runtime import build_runtime_measurement_adapter


ROOT = Path(__file__).resolve().parents[1]


def test_v3_22_10_runtime_measurement_adapter_is_read_only_over_records():
    records = [
        {
            "trial_index": 0,
            "reward": 1.0,
            "action": "left",
            "task_input": {"stimuli": {"tone": 1.0}, "available_actions": ["left", "right"]},
            "metadata": {"protocol_traces": {"emission": {"stimulus": {"tone": 1.0}}}},
        }
    ]
    before = deepcopy(records)

    adapter = build_runtime_measurement_adapter(preset_name="learning_curve_basic")
    out = adapter.step(records=records, metadata={"source": "boundary_test"})

    assert records == before
    assert out.metadata["runtime_measurement"]["preset_name"] == "learning_curve_basic"
    assert out.metadata["runtime_measurement"]["normalization"] == "runtime_measurement_records_v1"


def test_v3_22_10_runtime_measurement_replay_integration_is_post_run_only():
    program = compile_environment_program(
        {
            "phases": [
                {
                    "name": "Acquisition",
                    "protocol": "acquisition",
                    "stimuli": {"cs_plus": ["tone"]},
                    "params": {"n_trials": 2, "reward": 1.0},
                }
            ]
        }
    )
    env = CompiledProgramTestEnvironment(program)

    records, measurement = ReplayHarness().run_with_measurement(
        env,
        rollout_id="v3_22_10_measurement_boundary",
        episode_id=0,
        seed=9,
        measurement_preset_name="learning_curve_basic",
    )

    assert len(records) > 0
    assert measurement.metadata["runtime_measurement"]["preset_name"] == "learning_curve_basic"


def test_v3_22_10_runtime_measurement_surface_excludes_agent_protocol_mutators():
    text = (ROOT / "virtual_shaping_lab" / "vsl" / "runtime" / "measurement_adapter.py").read_text(
        encoding="utf-8"
    )
    forbidden = (
        ".learn(",
        ".act(",
        ".emit(",
        ".resolve(",
        "environment.step(",
    )
    for token in forbidden:
        assert token not in text
