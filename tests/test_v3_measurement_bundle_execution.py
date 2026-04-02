from __future__ import annotations

from virtual_shaping_lab.vsl.measurement import (
    LearningCurveBasicAnalysisOperator,
    LinePlotVisualizationOperator,
    MarkdownReportOperator,
    MeasurementBundle,
    MeasurementStepResult,
)


def _records() -> list[dict]:
    return [
        {"trial_index": 0, "reward": 1.0, "action": "left", "task_input": {"stimuli": {"tone": 1.0}}, "metadata": {}},
        {"trial_index": 1, "reward": 0.0, "action": "right", "task_input": {"stimuli": {"tone": 1.0}}, "metadata": {}},
    ]


def test_v3_22_5_measurement_bundle_step_order_and_traces():
    bundle = MeasurementBundle(
        analysis_operator=LearningCurveBasicAnalysisOperator(),
        visualization_operator=LinePlotVisualizationOperator(),
        report_operator=MarkdownReportOperator(),
    )
    out = bundle.step(records=_records(), metadata={"source": "test"})
    assert isinstance(out, MeasurementStepResult)
    assert out.metadata["pipeline_order"] == ["analyze", "visualize", "report", "finalize"]
    assert "analysis" in out.metadata["stage_traces"]
    assert "visualization" in out.metadata["stage_traces"]
    assert "report" in out.metadata["stage_traces"]
    assert out.report["format"] == "markdown"
