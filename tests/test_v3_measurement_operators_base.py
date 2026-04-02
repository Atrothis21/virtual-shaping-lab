from __future__ import annotations

from virtual_shaping_lab.vsl.measurement import (
    AnalysisOperator,
    AnalysisOutput,
    JsonReportOperator,
    LearningCurveBasicAnalysisOperator,
    LinePlotVisualizationOperator,
    MarkdownReportOperator,
    MeasurementStepResult,
    ReportOperator,
    VisualizationOperator,
    VisualizationOutput,
)


def test_v3_22_5_measurement_operator_protocol_runtime_checkable():
    assert isinstance(LearningCurveBasicAnalysisOperator(), AnalysisOperator)
    assert isinstance(LinePlotVisualizationOperator(), VisualizationOperator)
    assert isinstance(MarkdownReportOperator(), ReportOperator)
    assert isinstance(JsonReportOperator(), ReportOperator)


def test_v3_22_5_measurement_output_types_validate_shape():
    analysis = AnalysisOutput(metrics={"trial_count": 2}, metadata={"variant": "x"})
    visualization = VisualizationOutput(figures=[{"kind": "line"}], metadata={"variant": "y"})
    step = MeasurementStepResult(
        analysis=analysis,
        visualization=visualization,
        report={"format": "markdown"},
        metadata={"pipeline_order": ["analyze", "visualize", "report", "finalize"]},
    )
    assert step.analysis.metrics["trial_count"] == 2
    assert step.visualization.figures[0]["kind"] == "line"
    assert step.report["format"] == "markdown"
