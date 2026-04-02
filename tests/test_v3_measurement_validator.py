from __future__ import annotations

import pytest

from virtual_shaping_lab.vsl.measurement import MeasurementSpec, MeasurementSpecValidationError
from virtual_shaping_lab.vsl.measurement.validation import validate_measurement_spec


def _base_spec() -> MeasurementSpec:
    return MeasurementSpec(
        analysis_ops=["learning_curve_basic"],
        visualization_ops=["line_plot"],
        report_op="markdown_report",
    )


def test_v3_measurement_validator_accepts_valid_spec():
    validate_measurement_spec(_base_spec())


def test_v3_measurement_validator_rejects_unknown_analysis_operator():
    with pytest.raises(MeasurementSpecValidationError, match="MEAS_E_UNKNOWN_ANALYSIS_OP"):
        MeasurementSpec(
            analysis_ops=["unknown_analysis"],
            visualization_ops=["line_plot"],
            report_op="markdown_report",
        )


def test_v3_measurement_validator_rejects_unknown_visualization_operator():
    with pytest.raises(MeasurementSpecValidationError, match="MEAS_E_UNKNOWN_VISUALIZATION_OP"):
        MeasurementSpec(
            analysis_ops=["learning_curve_basic"],
            visualization_ops=["unknown_plot"],
            report_op="markdown_report",
        )


def test_v3_measurement_validator_rejects_unknown_report_operator():
    with pytest.raises(MeasurementSpecValidationError, match="MEAS_E_UNKNOWN_REPORT_OP"):
        MeasurementSpec(
            analysis_ops=["learning_curve_basic"],
            visualization_ops=["line_plot"],
            report_op="unknown_report",
        )


def test_v3_measurement_validator_rejects_empty_analysis_ops():
    with pytest.raises(MeasurementSpecValidationError, match="MEAS_E_EMPTY_ANALYSIS_OPS"):
        MeasurementSpec(
            analysis_ops=[],
            visualization_ops=["line_plot"],
            report_op="markdown_report",
        )


def test_v3_measurement_validator_rejects_report_visualization_requirement_mismatch():
    with pytest.raises(MeasurementSpecValidationError, match="MEAS_E_REPORT_REQUIRES_VISUALIZATION"):
        MeasurementSpec(
            analysis_ops=["learning_curve_basic"],
            visualization_ops=[],
            report_op="pdf_report",
        )


def test_v3_measurement_validator_rejects_analysis_visualization_mismatch():
    with pytest.raises(MeasurementSpecValidationError, match="MEAS_E_ANALYSIS_VISUALIZATION_MISMATCH"):
        MeasurementSpec(
            analysis_ops=["learning_curve_basic"],
            visualization_ops=["bar_plot"],
            report_op="markdown_report",
        )
