"""Measurement-grammar legality validator for V3.22.0."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

ANALYSIS_OP_VALUES = {
    "learning_curve_basic",
    "extinction_curve",
    "generalization_profile",
    "blocking_diagnostics",
    "action_learning_curve",
    "policy_diagnostics",
    "prediction_error_diagnostics",
}
VISUALIZATION_OP_VALUES = {
    "line_plot",
    "multi_line_plot",
    "heatmap_plot",
    "bar_plot",
}
REPORT_OP_VALUES = {"default_report", "pdf_report", "markdown_report", "json_report"}

ANALYSIS_TO_VISUALIZATION: dict[str, set[str]] = {
    "learning_curve_basic": {"line_plot"},
    "extinction_curve": {"line_plot"},
    "generalization_profile": {"line_plot", "heatmap_plot"},
    "blocking_diagnostics": {"multi_line_plot", "bar_plot"},
    "action_learning_curve": {"line_plot"},
    "policy_diagnostics": {"line_plot", "bar_plot"},
    "prediction_error_diagnostics": {"line_plot", "bar_plot"},
}

REPORT_REQUIRES_VISUALIZATION: dict[str, bool] = {
    "default_report": False,
    "pdf_report": True,
    "markdown_report": False,
    "json_report": False,
}


@dataclass
class MeasurementSpecValidationError(ValueError):
    code: str
    message: str

    def __str__(self) -> str:
        return f"[{self.code}] {self.message}"


def _reject(code: str, message: str) -> None:
    raise MeasurementSpecValidationError(code=code, message=message)


def validate_measurement_spec(spec: Any) -> None:
    analysis_ops = getattr(spec, "analysis_ops", None)
    visualization_ops = getattr(spec, "visualization_ops", None)
    report_op = getattr(spec, "report_op", None)
    metadata = getattr(spec, "metadata", None)

    if not isinstance(analysis_ops, list):
        _reject("MEAS_E_ANALYSIS_NOT_LIST", "MeasurementSpec.analysis_ops must be a list.")
    if not isinstance(visualization_ops, list):
        _reject("MEAS_E_VISUALIZATION_NOT_LIST", "MeasurementSpec.visualization_ops must be a list.")
    if not isinstance(metadata, dict):
        _reject("MEAS_E_METADATA_NOT_OBJECT", "MeasurementSpec.metadata must be an object.")

    for op in analysis_ops:
        if op not in ANALYSIS_OP_VALUES:
            _reject("MEAS_E_UNKNOWN_ANALYSIS_OP", f"Unsupported analysis operator '{op}'.")
    for op in visualization_ops:
        if op not in VISUALIZATION_OP_VALUES:
            _reject("MEAS_E_UNKNOWN_VISUALIZATION_OP", f"Unsupported visualization operator '{op}'.")
    if report_op not in REPORT_OP_VALUES:
        _reject("MEAS_E_UNKNOWN_REPORT_OP", f"Unsupported report operator '{report_op}'.")

    if not analysis_ops:
        _reject("MEAS_E_EMPTY_ANALYSIS_OPS", "MeasurementSpec.analysis_ops must include at least one operator.")

    if not visualization_ops and REPORT_REQUIRES_VISUALIZATION.get(report_op, False):
        _reject(
            "MEAS_E_REPORT_REQUIRES_VISUALIZATION",
            f"report_op '{report_op}' requires at least one visualization operator.",
        )

    visualization_set = set(visualization_ops)
    for analysis_op in analysis_ops:
        allowed_visualizations = ANALYSIS_TO_VISUALIZATION[analysis_op]
        if visualization_set and visualization_set.isdisjoint(allowed_visualizations):
            _reject(
                "MEAS_E_ANALYSIS_VISUALIZATION_MISMATCH",
                (
                    f"analysis operator '{analysis_op}' is incompatible with "
                    f"visualization_ops {sorted(visualization_set)}."
                ),
            )
