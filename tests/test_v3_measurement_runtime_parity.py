from __future__ import annotations

from virtual_shaping_lab.vsl.environment import CompiledProgramTestEnvironment
from virtual_shaping_lab.vsl.measurement import build_executable_measurement_preset
from virtual_shaping_lab.vsl.program import compile_environment_program
from virtual_shaping_lab.vsl.rollout import ReplayHarness
from virtual_shaping_lab.vsl.runtime import build_runtime_measurement_adapter


def _runtime_records() -> list[dict]:
    return [
        {
            "trial_index": 0,
            "reward": 1.0,
            "action": "left",
            "task_input": {"stimuli": {"tone": 1.0}, "available_actions": ["left", "right"]},
            "metadata": {"prediction_error": 0.5},
        },
        {
            "trial_index": 1,
            "reward": 0.0,
            "action": "right",
            "task_input": {"stimuli": {"tone": 1.0}, "available_actions": ["left", "right"]},
            "metadata": {"prediction_error": -0.5},
        },
    ]


def test_v3_22_10_runtime_measurement_adapter_matches_direct_bundle_for_normalized_records():
    runtime_adapter = build_runtime_measurement_adapter(preset_name="learning_curve_basic")
    executable = build_executable_measurement_preset("learning_curve_basic")

    runtime_out = runtime_adapter.step(records=_runtime_records(), metadata={"source": "runtime_parity_test"})
    direct_out = executable.bundle.step(
        records=_runtime_records(),
        metadata={
            "source": "runtime_parity_test",
            "runtime_measurement": {
                "preset_name": "learning_curve_basic",
                "normalization": "runtime_measurement_records_v1",
            },
        },
    )

    assert runtime_out.analysis.metrics == direct_out.analysis.metrics
    assert runtime_out.analysis.metadata == direct_out.analysis.metadata
    assert runtime_out.visualization.figures == direct_out.visualization.figures
    assert runtime_out.visualization.metadata == direct_out.visualization.metadata
    assert runtime_out.report == direct_out.report
    assert runtime_out.metadata == direct_out.metadata


def test_v3_22_10_runtime_measurement_adapter_is_deterministic_on_replay_records_with_fixed_seed():
    program = compile_environment_program(
        {
            "phases": [
                {
                    "name": "Acq",
                    "protocol": "acquisition",
                    "stimuli": {"cs_plus": ["tone"]},
                    "params": {"n_trials": 3, "outcome": 1.0},
                }
            ]
        }
    )
    env = CompiledProgramTestEnvironment(program)
    records = ReplayHarness().run(
        env,
        rollout_id="v3_22_10_measurement_parity",
        episode_id=1,
        seed=13,
    )

    runtime_adapter = build_runtime_measurement_adapter(preset_name="learning_curve_basic")
    measurement_records = ReplayHarness._records_to_runtime_measurement_payload(records)

    out_a = runtime_adapter.step(records=measurement_records, metadata={"source": "replay_parity"})
    out_b = runtime_adapter.step(records=measurement_records, metadata={"source": "replay_parity"})

    assert out_a.analysis.metrics == out_b.analysis.metrics
    assert out_a.visualization.figures == out_b.visualization.figures
    assert out_a.report == out_b.report
    assert out_a.metadata == out_b.metadata
