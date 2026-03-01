"""Unified analysis registries for metrics, figures, and reports."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from analysis.domain.types import AnalysisContext, FigureResult, MetricResult, ReportResult
from analysis.report.catalog import get_default_template_for_protocol
from analysis.verification import (
    MeanRewardMetric,
    ProbeBarFigure,
    TickResponseRateFigure,
    TrialCurveFigure,
    VerificationReport,
)


METRICS: dict[str, type] = {
    MeanRewardMetric.name: MeanRewardMetric,
}

FIGURES: dict[str, type] = {
    TrialCurveFigure.name: TrialCurveFigure,
    TickResponseRateFigure.name: TickResponseRateFigure,
    ProbeBarFigure.name: ProbeBarFigure,
}

REPORTS: dict[str, type] = {
    VerificationReport.name: VerificationReport,
}


def build_metric(name: str, **kwargs):
    if name not in METRICS:
        raise KeyError(f"Unknown metric '{name}'.")
    return METRICS[name](**kwargs)


def build_figure(name: str, **kwargs):
    if name not in FIGURES:
        raise KeyError(f"Unknown figure '{name}'.")
    return FIGURES[name](**kwargs)


def build_report(name: str, **kwargs):
    if name not in REPORTS:
        raise KeyError(f"Unknown report '{name}'.")
    return REPORTS[name](**kwargs)


def run_report_template(
    report_name: str,
    records: list[dict[str, Any]],
    out_dir: str,
    ctx: AnalysisContext | None = None,
) -> ReportResult:
    context = ctx or AnalysisContext.from_records(records)
    report = build_report(report_name)

    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    metrics: dict[str, MetricResult] = {}
    for metric_name in getattr(report, "metric_names", []):
        metric = build_metric(metric_name)
        result = metric.compute(records, context)
        metrics[result.name] = result

    figures: list[FigureResult] = []
    for figure_name in getattr(report, "figure_names", []):
        figure = build_figure(figure_name)
        result = figure.render(records, metrics, context, str(out_path))
        figures.append(result)

    return report.build(records, metrics, figures, context, str(out_path))


def run_protocol_default_report(
    protocol_name: str,
    records: list[dict[str, Any]],
    out_dir: str,
    ctx: AnalysisContext | None = None,
) -> ReportResult:
    template = get_default_template_for_protocol(protocol_name)
    context = ctx or AnalysisContext.from_records(records)

    report = build_report(template.report_name)
    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    metrics: dict[str, MetricResult] = {}
    for metric_name in template.metric_names:
        metric = build_metric(metric_name)
        result = metric.compute(records, context)
        metrics[result.name] = result

    figures: list[FigureResult] = []
    for figure_name in template.figure_names:
        figure = build_figure(figure_name)
        result = figure.render(records, metrics, context, str(out_path))
        figures.append(result)

    return report.build(records, metrics, figures, context, str(out_path))
