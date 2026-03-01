"""Analysis domain contracts."""

from analysis.domain.interfaces import IFigure, IMetric, IReport
from analysis.domain.types import AnalysisContext, FigureResult, MetricResult, ReportResult

__all__ = [
    "AnalysisContext",
    "MetricResult",
    "FigureResult",
    "ReportResult",
    "IMetric",
    "IFigure",
    "IReport",
]
