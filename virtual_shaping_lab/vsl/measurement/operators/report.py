"""Executable measurement report operators (deterministic summaries)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from virtual_shaping_lab.vsl.measurement.output import AnalysisOutput, VisualizationOutput


def _numeric_summary(metrics: Mapping[str, Any]) -> dict[str, float]:
    summary: dict[str, float] = {}
    for key in sorted(metrics.keys(), key=str):
        value = metrics[key]
        if isinstance(value, (int, float)):
            summary[str(key)] = float(value)
    return summary


@dataclass(frozen=True)
class MarkdownReportOperator:
    """Create deterministic markdown-style report payload."""

    slot: str = "M_report"
    variant: str = "markdown_report"

    def summarize(
        self,
        *,
        analysis: AnalysisOutput,
        visualization: VisualizationOutput,
        metadata: Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        _ = metadata
        numeric = _numeric_summary(analysis.metrics)
        highlights = [f"- {key}: {numeric[key]:.6g}" for key in sorted(numeric.keys())]
        return {
            "format": "markdown",
            "title": f"Measurement Report ({analysis.metadata.get('variant', 'analysis')})",
            "highlights": highlights,
            "figure_count": len(visualization.figures),
            "metadata": {"variant": self.variant, "slot": self.slot},
        }


@dataclass(frozen=True)
class JsonReportOperator:
    """Create deterministic json-style report payload."""

    slot: str = "M_report"
    variant: str = "json_report"

    def summarize(
        self,
        *,
        analysis: AnalysisOutput,
        visualization: VisualizationOutput,
        metadata: Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        _ = metadata
        return {
            "format": "json",
            "analysis_metrics": dict(analysis.metrics),
            "analysis_metadata": dict(analysis.metadata),
            "visualization_metadata": dict(visualization.metadata),
            "figure_count": len(visualization.figures),
            "metadata": {"variant": self.variant, "slot": self.slot},
        }


@dataclass(frozen=True)
class PdfReportOperator:
    """Create deterministic pdf-style report descriptor payload."""

    slot: str = "M_report"
    variant: str = "pdf_report"

    def summarize(
        self,
        *,
        analysis: AnalysisOutput,
        visualization: VisualizationOutput,
        metadata: Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        _ = metadata
        numeric = _numeric_summary(analysis.metrics)
        return {
            "format": "pdf_descriptor",
            "sections": [
                {"name": "analysis", "metric_keys": sorted(analysis.metrics.keys(), key=str)},
                {"name": "visualization", "figure_count": len(visualization.figures)},
                {"name": "summary", "numeric_keys": sorted(numeric.keys())},
            ],
            "metadata": {"variant": self.variant, "slot": self.slot},
        }
