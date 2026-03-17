import pytest

from analysis.domain.interfaces import IFigure, IMetric, IReport
from analysis.domain.types import AnalysisContext, FigureResult, MetricResult, ReportResult


class DummyMetric(IMetric):
    def compute(self, records, ctx):
        return MetricResult(name="dummy", value=len(records), meta={"mode": ctx.record_mode})


class DummyFigure(IFigure):
    def render(self, records, metrics, ctx, out_dir):
        return FigureResult(name="dummy_fig", path=f"{out_dir}/dummy.png", meta={"count": len(metrics)})


class DummyReport(IReport):
    def build(self, records, metrics, figures, ctx, out_dir):
        return ReportResult(name="dummy_report", output_dir=out_dir, artifacts={"n_figs": len(figures)})


def test_analysis_context_from_records_tick_and_trial():
    trial_ctx = AnalysisContext.from_records([{"trial": 0, "metadata": {"plan_hash": "abc"}}])
    assert trial_ctx.record_mode == "trial"
    assert trial_ctx.plan_hash == "abc"

    tick_ctx = AnalysisContext.from_records([{"trial": 0, "tick": 0, "dt_s": 0.1, "unit_path": "p.q"}])
    assert tick_ctx.record_mode == "tick"
    assert tick_ctx.dt_s == 0.1
    assert tick_ctx.protocol_path == "p.q"


def test_analysis_interfaces_contract_execution(tmp_path):
    ctx = AnalysisContext(record_mode="trial")
    metric = DummyMetric().compute([{"trial": 0}, {"trial": 1}], ctx)
    assert metric == MetricResult(name="dummy", value=2, meta={"mode": "trial"})

    fig = DummyFigure().render([], {"dummy": metric}, ctx, str(tmp_path))
    assert fig.name == "dummy_fig"
    assert fig.path.endswith("dummy.png")

    report = DummyReport().build([], {"dummy": metric}, [fig], ctx, str(tmp_path))
    assert report == ReportResult(name="dummy_report", output_dir=str(tmp_path), artifacts={"n_figs": 1})


def test_analysis_context_from_empty_records():
    ctx = AnalysisContext.from_records([])
    assert ctx == AnalysisContext()


def test_analysis_context_accepts_minimum_record_schema_fields():
    ctx = AnalysisContext.from_records(
        [
            {
                "trial": 0,
                "step": 0,
                "tick": 0,
                "stimulus": None,
                "action": None,
                "reward": 0.0,
                "prediction": 0.1,
                "prediction_error": -0.1,
                "policy_state": None,
                "metadata": {},
            }
        ]
    )
    assert ctx.record_mode == "tick"
