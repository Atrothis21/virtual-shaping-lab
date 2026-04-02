from __future__ import annotations

import pytest

from virtual_shaping_lab.vsl.measurement import MeasurementSpec
from virtual_shaping_lab.vsl.measurement.executable_presets import (
    ExecutableMeasurementPreset,
    build_executable_measurement_from_spec,
    build_executable_measurement_preset,
    executable_measurement_preset_names,
)


def test_v3_22_5_executable_measurement_preset_names_cover_registry():
    assert executable_measurement_preset_names() == [
        "action_learning_curve",
        "blocking_diagnostics",
        "extinction_curve",
        "generalization_profile",
        "learning_curve_basic",
        "policy_diagnostics",
        "prediction_error_diagnostics",
    ]


def test_v3_22_5_build_executable_measurement_preset_smoke():
    preset = build_executable_measurement_preset("learning_curve_basic")
    assert isinstance(preset, ExecutableMeasurementPreset)
    assert preset.preset_name == "learning_curve_basic"
    out = preset.bundle.step(records=[{"trial_index": 0, "reward": 1.0, "action": "left", "task_input": {}, "metadata": {}}])
    assert out.report["format"] == "markdown"


def test_v3_22_5_build_executable_measurement_from_spec_supported_mapping():
    spec = MeasurementSpec(
        analysis_ops=["prediction_error_diagnostics"],
        visualization_ops=["line_plot"],
        report_op="json_report",
    )
    preset = build_executable_measurement_from_spec(spec)
    assert preset.measurement_spec.analysis_ops == ["prediction_error_diagnostics"]
    out = preset.bundle.step(records=[{"trial_index": 0, "reward": 0.0, "action": None, "task_input": {}, "metadata": {}}])
    assert out.report["format"] == "json"


def test_v3_22_5_build_executable_measurement_preset_rejects_unknown():
    with pytest.raises(ValueError, match="MEAS_E_UNKNOWN_PRESET"):
        build_executable_measurement_preset("unknown_preset")
