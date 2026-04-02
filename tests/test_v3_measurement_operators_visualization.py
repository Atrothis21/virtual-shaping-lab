from __future__ import annotations

from virtual_shaping_lab.vsl.measurement import (
    AnalysisOutput,
    BarPlotVisualizationOperator,
    HeatmapVisualizationOperator,
    JsonReportOperator,
    LinePlotVisualizationOperator,
    MarkdownReportOperator,
    MultiLinePlotVisualizationOperator,
    PdfReportOperator,
)


def _analysis() -> AnalysisOutput:
    return AnalysisOutput(
        metrics={
            "reward_curve": [1.0, 0.5, 0.25],
            "action_counts": {"left": 2, "right": 1},
            "cue_reward_mean": {"tone": 0.8, "noise": 0.2},
            "trial_count": 3,
            "mean_reward": 0.5833333333,
        },
        metadata={"variant": "learning_curve_basic"},
    )


def test_v3_22_5_visualization_operators_emit_deterministic_payloads():
    analysis = _analysis()
    line = LinePlotVisualizationOperator().visualize(analysis=analysis)
    multi = MultiLinePlotVisualizationOperator().visualize(analysis=analysis)
    bar = BarPlotVisualizationOperator().visualize(analysis=analysis)
    heatmap = HeatmapVisualizationOperator().visualize(analysis=analysis)

    assert line.figures[0]["kind"] == "line"
    assert multi.figures[0]["kind"] == "multi_line"
    assert bar.figures[0]["kind"] == "bar"
    assert heatmap.figures[0]["kind"] == "heatmap"


def test_v3_22_5_report_operators_emit_deterministic_payloads():
    analysis = _analysis()
    visualization = LinePlotVisualizationOperator().visualize(analysis=analysis)
    markdown = MarkdownReportOperator().summarize(analysis=analysis, visualization=visualization)
    as_json = JsonReportOperator().summarize(analysis=analysis, visualization=visualization)
    as_pdf = PdfReportOperator().summarize(analysis=analysis, visualization=visualization)

    assert markdown["format"] == "markdown"
    assert as_json["format"] == "json"
    assert as_pdf["format"] == "pdf_descriptor"
    assert markdown["figure_count"] == 1
    assert as_json["figure_count"] == 1
