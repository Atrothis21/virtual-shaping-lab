"""Executable measurement operator protocols."""

from __future__ import annotations

from typing import Any, Mapping, Protocol, Sequence, runtime_checkable

from virtual_shaping_lab.vsl.measurement.output import AnalysisOutput, VisualizationOutput


@runtime_checkable
class AnalysisOperator(Protocol):
    """Compute measurement metrics from canonical rollout records and traces."""

    def analyze(
        self,
        *,
        records: Sequence[Mapping[str, Any]],
        metadata: Mapping[str, Any] | None = None,
    ) -> AnalysisOutput: ...


@runtime_checkable
class VisualizationOperator(Protocol):
    """Render deterministic visualization artifacts from analysis output."""

    def visualize(
        self,
        *,
        analysis: AnalysisOutput,
        metadata: Mapping[str, Any] | None = None,
    ) -> VisualizationOutput: ...


@runtime_checkable
class ReportOperator(Protocol):
    """Build final report payload from analysis and visualization outputs."""

    def summarize(
        self,
        *,
        analysis: AnalysisOutput,
        visualization: VisualizationOutput,
        metadata: Mapping[str, Any] | None = None,
    ) -> dict[str, Any]: ...
