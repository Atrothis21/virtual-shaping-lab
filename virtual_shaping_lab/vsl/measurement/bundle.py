"""Executable measurement bundle orchestration (V3.22.5 slice 4)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Sequence

from virtual_shaping_lab.vsl.contracts import TrialRecord
from virtual_shaping_lab.vsl.measurement.operators import AnalysisOperator, ReportOperator, VisualizationOperator
from virtual_shaping_lab.vsl.measurement.output import AnalysisOutput, MeasurementStepResult, VisualizationOutput


def _coerce_analysis_output(value: Any) -> AnalysisOutput:
    if isinstance(value, AnalysisOutput):
        return value
    if isinstance(value, Mapping):
        return AnalysisOutput(
            metrics=dict(value.get("metrics", {})),
            metadata=dict(value.get("metadata", {})),
        )
    raise ValueError("Analysis operator must return AnalysisOutput or mapping payload.")


def _coerce_visualization_output(value: Any) -> VisualizationOutput:
    if isinstance(value, VisualizationOutput):
        return value
    if isinstance(value, Mapping):
        figures = value.get("figures", [])
        metadata = value.get("metadata", {})
        return VisualizationOutput(
            figures=list(figures) if isinstance(figures, (list, tuple)) else [],
            metadata=dict(metadata) if isinstance(metadata, Mapping) else {},
        )
    raise ValueError("Visualization operator must return VisualizationOutput or mapping payload.")


@dataclass
class MeasurementBundle:
    """
    Canonical executable measurement order:
    1) analyze
    2) visualize
    3) report
    4) finalize typed MeasurementStepResult
    """

    analysis_operator: AnalysisOperator
    visualization_operator: VisualizationOperator
    report_operator: ReportOperator

    def step(
        self,
        *,
        records: Sequence[TrialRecord | Mapping[str, Any]],
        metadata: Mapping[str, Any] | None = None,
    ) -> MeasurementStepResult:
        incoming_metadata = dict(metadata or {})

        analysis_raw = self.analysis_operator.analyze(
            records=records,
            metadata=incoming_metadata,
        )
        analysis = _coerce_analysis_output(analysis_raw)

        visualization_raw = self.visualization_operator.visualize(
            analysis=analysis,
            metadata=incoming_metadata,
        )
        visualization = _coerce_visualization_output(visualization_raw)

        report = self.report_operator.summarize(
            analysis=analysis,
            visualization=visualization,
            metadata=incoming_metadata,
        )
        if not isinstance(report, Mapping):
            raise ValueError("Report operator must return mapping payload.")
        report_payload = dict(report)

        stage_traces = {
            "analysis": {
                "metric_keys": sorted(analysis.metrics.keys(), key=str),
                "metadata": dict(analysis.metadata),
            },
            "visualization": {
                "figure_count": len(visualization.figures),
                "metadata": dict(visualization.metadata),
            },
            "report": {
                "keys": sorted(report_payload.keys(), key=str),
            },
        }
        pipeline_order = ["analyze", "visualize", "report", "finalize"]

        return MeasurementStepResult(
            analysis=analysis,
            visualization=visualization,
            report=report_payload,
            metadata={
                **incoming_metadata,
                "stage_traces": stage_traces,
                "pipeline_order": pipeline_order,
            },
        )
