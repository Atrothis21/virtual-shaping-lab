import json
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass

from analysis.report.presets import get_report_preset
from analysis.metrics.registry import METRIC_REGISTRY
from analysis.visualizations.registry import VISUALIZATION_REGISTRY
from analysis.report.pdf import ReportPDF
from paths import REPORTS_DIR

DEFAULT_REPORTS_DIR = REPORTS_DIR


def _to_jsonable(value):
    if isinstance(value, dict):
        return {str(k): _to_jsonable(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_to_jsonable(v) for v in value]
    if isinstance(value, tuple):
        return [_to_jsonable(v) for v in value]
    return value


@dataclass(frozen=True)
class ReportRunContext:
    report_dir: Path
    metrics_dir: Path


class ReportArtifactWriter:
    def create_context(self, *, output_dir: str | None = None) -> ReportRunContext:
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        base_dir = Path(output_dir) if output_dir is not None else DEFAULT_REPORTS_DIR
        report_dir = base_dir / timestamp
        report_dir.mkdir(parents=True, exist_ok=False)
        metrics_dir = report_dir / "metrics"
        metrics_dir.mkdir(parents=True, exist_ok=True)
        return ReportRunContext(report_dir=report_dir, metrics_dir=metrics_dir)

    def write_provenance(self, *, records, payload, ctx: ReportRunContext) -> None:
        if payload is not None:
            with open(ctx.report_dir / "payload.json", "w") as f:
                json.dump(payload, f, indent=2)
            attention = payload.get("experiment", {}).get("attention")
            if isinstance(attention, dict):
                with open(ctx.report_dir / "attention_summary.json", "w") as f:
                    json.dump(attention, f, indent=2)

        with open(ctx.report_dir / "records.json", "w") as f:
            json.dump(records, f, indent=2)

    def write_metric_output(self, *, metric_name: str, result, ctx: ReportRunContext) -> None:
        with open(ctx.metrics_dir / f"{metric_name}.json", "w") as f:
            json.dump(_to_jsonable(result), f, indent=2)


class MetricExecutionPipeline:
    def run(self, *, records, report_config, artifact_writer: ReportArtifactWriter, ctx: ReportRunContext) -> dict:
        metrics = {}
        for metric_name in report_config.metrics:
            if metric_name not in METRIC_REGISTRY:
                raise KeyError(f"Unknown metric '{metric_name}'")

            metric_cls = METRIC_REGISTRY[metric_name]
            metric_kwargs = report_config.params.get(metric_name, {})
            metric = metric_cls(**metric_kwargs)
            metrics[metric_name] = metric.compute(records)
            artifact_writer.write_metric_output(metric_name=metric_name, result=metrics[metric_name], ctx=ctx)
        return metrics


class VisualizationPipeline:
    @staticmethod
    def _filtered_records(records, phase_names):
        if not phase_names:
            return records
        return [
            r for r in records
            if r.get("phase") in phase_names
            or r.get("phase_name") in phase_names
            or r.get("subphase_name") in phase_names
        ]

    def run(self, *, records, metrics, report_config, ctx: ReportRunContext, pdf: ReportPDF) -> list[str]:
        figures: list[str] = []
        for viz_name in report_config.visualizations:
            if viz_name not in VISUALIZATION_REGISTRY:
                raise KeyError(f"Unknown visualization '{viz_name}'")
            viz_cls = VISUALIZATION_REGISTRY[viz_name]
            viz = viz_cls()

            viz_params = report_config.params.get(viz_name, {})
            filtered_records = self._filtered_records(records, viz_params.get("phase_names"))
            viz.render(records=filtered_records, metrics=metrics)

            fig_path = ctx.report_dir / f"{viz_name}.png"
            if getattr(viz, "fig", None) is not None:
                pdf.add_figure(viz.fig, viz_name)
            viz.save(fig_path)
            figures.append(str(fig_path))
        return figures


class PdfComposer:
    def create(self, *, ctx: ReportRunContext) -> ReportPDF:
        return ReportPDF(ctx.report_dir / "report.pdf")

    def add_metric_pages(self, *, pdf: ReportPDF, metrics: dict) -> None:
        for metric_name, metric_result in metrics.items():
            pdf.add_metric_text(metric_name, _to_jsonable(metric_result))

    def close(self, *, pdf: ReportPDF) -> None:
        pdf.close()


def run_report(records, preset: str, payload=None, output_dir: str | None = None):
    """Generate analysis outputs and figures from experiment records."""
    report_config = get_report_preset(preset)

    artifact_writer = ReportArtifactWriter()
    metric_pipeline = MetricExecutionPipeline()
    viz_pipeline = VisualizationPipeline()
    pdf_composer = PdfComposer()

    ctx = artifact_writer.create_context(output_dir=output_dir)
    artifact_writer.write_provenance(records=records, payload=payload, ctx=ctx)

    metrics = metric_pipeline.run(
        records=records,
        report_config=report_config,
        artifact_writer=artifact_writer,
        ctx=ctx,
    )

    pdf = pdf_composer.create(ctx=ctx)
    _figures = viz_pipeline.run(
        records=records,
        metrics=metrics,
        report_config=report_config,
        ctx=ctx,
        pdf=pdf,
    )
    pdf_composer.add_metric_pages(pdf=pdf, metrics=metrics)
    pdf_composer.close(pdf=pdf)

    return ctx.report_dir
