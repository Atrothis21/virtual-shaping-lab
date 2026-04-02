"""Executable measurement visualization operators (deterministic payloads)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from virtual_shaping_lab.vsl.measurement.output import AnalysisOutput, VisualizationOutput


def _coerce_sequence(value: Any) -> list[Any]:
    if isinstance(value, (list, tuple)):
        return list(value)
    return []


def _coerce_mapping(value: Any) -> dict[str, Any]:
    if isinstance(value, Mapping):
        return {str(key): value[key] for key in sorted(value.keys(), key=str)}
    return {}


@dataclass(frozen=True)
class LinePlotVisualizationOperator:
    """Build deterministic line-plot payload from analysis metrics."""

    slot: str = "M_visualization"
    variant: str = "line_plot"

    def visualize(
        self,
        *,
        analysis: AnalysisOutput,
        metadata: Mapping[str, Any] | None = None,
    ) -> VisualizationOutput:
        _ = metadata
        metrics = dict(analysis.metrics)
        y_values = _coerce_sequence(metrics.get("reward_curve"))
        if not y_values:
            y_values = _coerce_sequence(metrics.get("prediction_error_curve"))
        if not y_values:
            y_values = _coerce_sequence(metrics.get("policy_entropy_curve"))
        figure = {
            "kind": "line",
            "x": list(range(len(y_values))),
            "y": y_values,
            "label": str(analysis.metadata.get("variant", "analysis")),
        }
        return VisualizationOutput(
            figures=[figure],
            metadata={"variant": self.variant, "slot": self.slot},
        )


@dataclass(frozen=True)
class MultiLinePlotVisualizationOperator:
    """Build deterministic multi-line payload from keyed metric series."""

    slot: str = "M_visualization"
    variant: str = "multi_line_plot"

    def visualize(
        self,
        *,
        analysis: AnalysisOutput,
        metadata: Mapping[str, Any] | None = None,
    ) -> VisualizationOutput:
        _ = metadata
        metrics = dict(analysis.metrics)
        keyed = _coerce_mapping(metrics.get("cue_reward_mean"))
        lines = [{"label": key, "x": [0], "y": [float(value)]} for key, value in keyed.items()]
        if not lines:
            action_counts = _coerce_mapping(metrics.get("action_counts"))
            lines = [{"label": key, "x": [0], "y": [float(value)]} for key, value in action_counts.items()]
        figure = {"kind": "multi_line", "lines": lines}
        return VisualizationOutput(
            figures=[figure],
            metadata={"variant": self.variant, "slot": self.slot},
        )


@dataclass(frozen=True)
class BarPlotVisualizationOperator:
    """Build deterministic bar-plot payload from keyed scalar metrics."""

    slot: str = "M_visualization"
    variant: str = "bar_plot"

    def visualize(
        self,
        *,
        analysis: AnalysisOutput,
        metadata: Mapping[str, Any] | None = None,
    ) -> VisualizationOutput:
        _ = metadata
        metrics = dict(analysis.metrics)
        values = _coerce_mapping(metrics.get("action_counts"))
        if not values:
            values = _coerce_mapping(metrics.get("cue_count"))
        bars = [{"label": key, "value": float(values[key])} for key in sorted(values.keys())]
        figure = {"kind": "bar", "bars": bars}
        return VisualizationOutput(
            figures=[figure],
            metadata={"variant": self.variant, "slot": self.slot},
        )


@dataclass(frozen=True)
class HeatmapVisualizationOperator:
    """Build deterministic heatmap payload from keyed scalar metrics."""

    slot: str = "M_visualization"
    variant: str = "heatmap_plot"

    def visualize(
        self,
        *,
        analysis: AnalysisOutput,
        metadata: Mapping[str, Any] | None = None,
    ) -> VisualizationOutput:
        _ = metadata
        metrics = dict(analysis.metrics)
        matrix_source = _coerce_mapping(metrics.get("cue_reward_mean"))
        keys = sorted(matrix_source.keys())
        values = [float(matrix_source[key]) for key in keys]
        figure = {
            "kind": "heatmap",
            "x_labels": keys,
            "y_labels": ["metric"],
            "z": [values],
        }
        return VisualizationOutput(
            figures=[figure],
            metadata={"variant": self.variant, "slot": self.slot},
        )
