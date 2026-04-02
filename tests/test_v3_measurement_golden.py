from __future__ import annotations

from virtual_shaping_lab.vsl.measurement.executable_presets import build_executable_measurement_preset


def _records() -> list[dict]:
    return [
        {
            "trial_index": 0,
            "reward": 1.0,
            "action": "left",
            "task_input": {"stimuli": {"tone": 1.0}},
            "metadata": {"prediction_error": 0.5, "policy_traces": {"action_probabilities": {"left": 0.8, "right": 0.2}}},
        },
        {
            "trial_index": 1,
            "reward": 0.0,
            "action": "right",
            "task_input": {"stimuli": {"tone": 1.0, "noise": 0.4}},
            "metadata": {"prediction_error": -0.25, "policy_traces": {"action_probabilities": {"left": 0.3, "right": 0.7}}},
        },
    ]


def test_v3_22_5_learning_curve_basic_golden():
    preset = build_executable_measurement_preset("learning_curve_basic")
    out = preset.bundle.step(records=_records())
    assert out.analysis.metrics["reward_curve"] == [1.0, 0.0]
    assert out.analysis.metrics["cumulative_reward_curve"] == [1.0, 1.0]
    assert out.report["format"] == "markdown"


def test_v3_22_5_prediction_error_diagnostics_golden():
    preset = build_executable_measurement_preset("prediction_error_diagnostics")
    out = preset.bundle.step(records=_records())
    assert out.analysis.metrics["prediction_error_curve"] == [0.5, -0.25]
    assert out.report["format"] == "markdown"


def test_v3_22_5_policy_diagnostics_golden():
    preset = build_executable_measurement_preset("policy_diagnostics")
    out = preset.bundle.step(records=_records())
    assert out.analysis.metrics["action_counts"] == {"left": 1, "right": 1}
    assert out.report["format"] == "json"
