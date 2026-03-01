"""Minimal verification report components for protocol/runtime validation."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt

from analysis.domain.interfaces import IFigure, IMetric, IReport
from analysis.domain.types import AnalysisContext, FigureResult, MetricResult, ReportResult
from analysis.views import aggregate_ticks_to_trials, tick_view, trial_view


class MeanRewardMetric(IMetric):
    name = "mean_reward"

    def compute(self, records: list[dict[str, Any]], ctx: AnalysisContext) -> MetricResult:
        rows = trial_view(records)
        if not rows:
            rows = aggregate_ticks_to_trials(tick_view(records))
        rewards = [float(r.get("reward", 0.0) or 0.0) for r in rows]
        mean = (sum(rewards) / len(rewards)) if rewards else 0.0
        return MetricResult(name=self.name, value=mean, series=rewards, meta={"n_trials": len(rewards)})


class TrialCurveFigure(IFigure):
    name = "trial_curve"

    def render(
        self,
        records: list[dict[str, Any]],
        metrics: dict[str, MetricResult],
        ctx: AnalysisContext,
        out_dir: str,
    ) -> FigureResult:
        rows = trial_view(records)
        if not rows:
            rows = aggregate_ticks_to_trials(tick_view(records))

        rewards = [float(r.get("reward", 0.0) or 0.0) for r in rows]
        preds = [r.get("prediction") for r in rows]
        preds_clean = [float(p) if p is not None else None for p in preds]
        x = list(range(len(rows)))

        fig, ax = plt.subplots(figsize=(6, 3))
        ax.plot(x, rewards, label="reward", linewidth=2)
        if any(p is not None for p in preds_clean):
            y = [p if p is not None else float("nan") for p in preds_clean]
            ax.plot(x, y, label="prediction", linewidth=2)
        ax.set_title("Trial Curve")
        ax.set_xlabel("trial")
        ax.legend(loc="best")

        output = Path(out_dir) / f"{self.name}.png"
        fig.tight_layout()
        fig.savefig(output)
        plt.close(fig)
        return FigureResult(name=self.name, path=str(output), meta={"n_trials": len(rows)})


class TickResponseRateFigure(IFigure):
    name = "tick_response_curve"

    def render(
        self,
        records: list[dict[str, Any]],
        metrics: dict[str, MetricResult],
        ctx: AnalysisContext,
        out_dir: str,
    ) -> FigureResult:
        ticks = tick_view(records)
        by_tick: dict[int, list[float]] = {}
        for row in ticks:
            tick = int(row.get("tick", 0) or 0)
            responded = 1.0 if row.get("action") is not None else 0.0
            by_tick.setdefault(tick, []).append(responded)

        xs = sorted(by_tick.keys())
        rates = [(sum(by_tick[t]) / len(by_tick[t])) for t in xs]

        fig, ax = plt.subplots(figsize=(6, 3))
        if xs:
            ax.plot(xs, rates, linewidth=2)
        ax.set_title("Within-Trial Response Rate")
        ax.set_xlabel("tick")
        ax.set_ylabel("response rate")

        output = Path(out_dir) / f"{self.name}.png"
        fig.tight_layout()
        fig.savefig(output)
        plt.close(fig)
        return FigureResult(name=self.name, path=str(output), meta={"n_ticks": len(xs)})


class ProbeBarFigure(IFigure):
    name = "probe_bar"

    def render(
        self,
        records: list[dict[str, Any]],
        metrics: dict[str, MetricResult],
        ctx: AnalysisContext,
        out_dir: str,
    ) -> FigureResult:
        rows = trial_view(records)
        if not rows:
            rows = aggregate_ticks_to_trials(tick_view(records))

        by_stimulus: dict[str, float] = {}
        for row in rows:
            stim = row.get("stimulus")
            pred = row.get("prediction")
            if stim is None or pred is None:
                continue
            key = str(stim)
            by_stimulus[key] = float(pred)

        labels = list(by_stimulus.keys())
        values = [by_stimulus[k] for k in labels]

        fig, ax = plt.subplots(figsize=(6, 3))
        if labels:
            ax.bar(labels, values)
        ax.set_title("Final Probe Values")
        ax.set_xlabel("stimulus")
        ax.set_ylabel("value")

        output = Path(out_dir) / f"{self.name}.png"
        fig.tight_layout()
        fig.savefig(output)
        plt.close(fig)
        return FigureResult(name=self.name, path=str(output), meta={"n_bars": len(labels)})


class VerificationReport(IReport):
    name = "verification_report"
    metric_names = ["mean_reward"]
    figure_names = ["trial_curve", "tick_response_curve", "probe_bar"]

    def build(
        self,
        records: list[dict[str, Any]],
        metrics: dict[str, MetricResult],
        figures: list[FigureResult],
        ctx: AnalysisContext,
        out_dir: str,
    ) -> ReportResult:
        return ReportResult(
            name=self.name,
            output_dir=out_dir,
            artifacts={
                "metrics": {k: v.value for k, v in metrics.items()},
                "figures": [f.path for f in figures],
            },
            meta={"record_mode": ctx.record_mode},
        )
