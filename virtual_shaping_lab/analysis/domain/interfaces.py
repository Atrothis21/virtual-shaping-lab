"""Analysis-layer interfaces."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from analysis.domain.types import AnalysisContext, FigureResult, MetricResult, ReportResult


class IMetric(ABC):
    @abstractmethod
    def compute(self, records: list[dict[str, Any]], ctx: AnalysisContext) -> MetricResult:
        raise NotImplementedError


class IFigure(ABC):
    @abstractmethod
    def render(
        self,
        records: list[dict[str, Any]],
        metrics: dict[str, MetricResult],
        ctx: AnalysisContext,
        out_dir: str,
    ) -> FigureResult:
        raise NotImplementedError


class IReport(ABC):
    @abstractmethod
    def build(
        self,
        records: list[dict[str, Any]],
        metrics: dict[str, MetricResult],
        figures: list[FigureResult],
        ctx: AnalysisContext,
        out_dir: str,
    ) -> ReportResult:
        raise NotImplementedError
