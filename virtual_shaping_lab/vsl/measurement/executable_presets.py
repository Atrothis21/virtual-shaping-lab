"""Executable measurement presets for V3.22.5 measurement core."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from .bundle import MeasurementBundle
from .operators import (
    BarPlotVisualizationOperator,
    BlockingDiagnosticsAnalysisOperator,
    HeatmapVisualizationOperator,
    JsonReportOperator,
    LearningCurveBasicAnalysisOperator,
    LinePlotVisualizationOperator,
    MarkdownReportOperator,
    MultiLinePlotVisualizationOperator,
    PdfReportOperator,
    PolicyDiagnosticsAnalysisOperator,
    PredictionErrorDiagnosticsAnalysisOperator,
)
from .presets import expand_measurement_preset, measurement_preset_names
from .spec import MeasurementSpec


@dataclass(frozen=True)
class ExecutableMeasurementPreset:
    """Resolved executable measurement preset payload."""

    preset_name: str
    measurement_spec: MeasurementSpec
    bundle: MeasurementBundle


def executable_measurement_preset_names() -> list[str]:
    return measurement_preset_names()


def _coerce_measurement_spec(spec: MeasurementSpec | Mapping[str, Any]) -> MeasurementSpec:
    if isinstance(spec, MeasurementSpec):
        return spec
    if isinstance(spec, Mapping):
        return MeasurementSpec.from_dict(dict(spec))
    raise TypeError("spec must be MeasurementSpec or object payload.")


def _resolve_analysis_operator(name: str) -> Any:
    if name in {"learning_curve_basic", "extinction_curve", "action_learning_curve"}:
        return LearningCurveBasicAnalysisOperator(variant=name)
    if name == "prediction_error_diagnostics":
        return PredictionErrorDiagnosticsAnalysisOperator()
    if name == "policy_diagnostics":
        return PolicyDiagnosticsAnalysisOperator()
    if name in {"blocking_diagnostics", "generalization_profile"}:
        return BlockingDiagnosticsAnalysisOperator(variant=name)
    raise ValueError(
        "[MEAS_E_EXECUTABLE_UNSUPPORTED_SPEC] Symbolic measurement spec is legal but does not map "
        "to a V3.22.5 executable core analysis operator."
    )


def _resolve_visualization_operator(name: str) -> Any:
    if name == "line_plot":
        return LinePlotVisualizationOperator()
    if name == "multi_line_plot":
        return MultiLinePlotVisualizationOperator()
    if name == "bar_plot":
        return BarPlotVisualizationOperator()
    if name == "heatmap_plot":
        return HeatmapVisualizationOperator()
    raise ValueError(
        "[MEAS_E_EXECUTABLE_UNSUPPORTED_SPEC] Symbolic measurement spec is legal but does not map "
        "to a V3.22.5 executable core visualization operator."
    )


def _resolve_report_operator(name: str) -> Any:
    if name in {"default_report", "markdown_report"}:
        return MarkdownReportOperator(variant=name)
    if name == "json_report":
        return JsonReportOperator()
    if name == "pdf_report":
        return PdfReportOperator()
    raise ValueError(
        "[MEAS_E_EXECUTABLE_UNSUPPORTED_SPEC] Symbolic measurement spec is legal but does not map "
        "to a V3.22.5 executable core report operator."
    )


def build_executable_measurement_preset(
    preset_name: str,
) -> ExecutableMeasurementPreset:
    """Materialize executable measurement bundle presets."""
    spec = expand_measurement_preset(preset_name)
    return build_executable_measurement_from_spec(spec)


def build_executable_measurement_from_spec(
    spec: MeasurementSpec | Mapping[str, Any],
) -> ExecutableMeasurementPreset:
    """Materialize executable measurement bundle directly from legal symbolic measurement spec."""
    measurement_spec = _coerce_measurement_spec(spec)

    preset_name = str(measurement_spec.metadata.get("preset_name", "")).strip()
    if preset_name not in executable_measurement_preset_names():
        preset_name = "custom_measurement"

    if not measurement_spec.analysis_ops:
        raise ValueError(
            "[MEAS_E_EXECUTABLE_UNSUPPORTED_SPEC] Symbolic measurement spec is legal but missing analysis operators."
        )
    if not measurement_spec.visualization_ops:
        raise ValueError(
            "[MEAS_E_EXECUTABLE_UNSUPPORTED_SPEC] Symbolic measurement spec is legal but missing visualization operators."
        )

    analysis_operator = _resolve_analysis_operator(measurement_spec.analysis_ops[0])
    visualization_operator = _resolve_visualization_operator(measurement_spec.visualization_ops[0])
    report_operator = _resolve_report_operator(measurement_spec.report_op)

    bundle = MeasurementBundle(
        analysis_operator=analysis_operator,
        visualization_operator=visualization_operator,
        report_operator=report_operator,
    )
    return ExecutableMeasurementPreset(
        preset_name=preset_name,
        measurement_spec=measurement_spec,
        bundle=bundle,
    )
