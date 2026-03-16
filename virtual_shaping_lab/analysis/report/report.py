import json
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass

from analysis.report.presets import get_report_preset
from analysis.metrics.registry import METRIC_REGISTRY
from analysis.visualizations.registry import VISUALIZATION_REGISTRY
from analysis.report.pdf import ReportPDF
from paths import REPORTS_DIR
from experiment.payload_contract import to_canonical_payload

DEFAULT_REPORTS_DIR = REPORTS_DIR


def _to_jsonable(value):
    if isinstance(value, dict):
        return {str(k): _to_jsonable(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_to_jsonable(v) for v in value]
    if isinstance(value, tuple):
        return [_to_jsonable(v) for v in value]
    return value


def _extract_mechanism_provenance(payload):
    if not isinstance(payload, dict):
        return None

    provenance = payload.get("provenance")
    if isinstance(provenance, dict) and isinstance(provenance.get("mechanisms"), dict):
        return provenance.get("mechanisms")

    plan = payload.get("plan")
    if not isinstance(plan, dict):
        return None
    settings = plan.get("settings")
    if not isinstance(settings, dict):
        return None
    composed = settings.get("composed_parameters")
    if not isinstance(composed, dict):
        return None

    representation = composed.get("representation", {}) if isinstance(composed.get("representation"), dict) else {}
    learner = composed.get("learner", {}) if isinstance(composed.get("learner"), dict) else {}
    policy = composed.get("policy", {}) if isinstance(composed.get("policy"), dict) else {}

    temporal_basis = representation.get("temporal_basis", {})
    if not isinstance(temporal_basis, dict):
        temporal_basis = {}
    temporal_variant = temporal_basis.get("variant", "identity")
    if not temporal_basis.get("enabled", False):
        temporal_variant = "none"

    similarity_kernel = representation.get("similarity_kernel", {})
    if not isinstance(similarity_kernel, dict):
        similarity_kernel = {}
    similarity_variant = similarity_kernel.get("variant", "matrix")
    if not similarity_kernel.get("enabled", False):
        similarity_variant = "identity"

    return {
        "context_map": {"variant": representation.get("context_map", {}).get("variant", "gated")},
        "similarity_kernel": {"variant": similarity_variant},
        "salience_operator": {"variant": representation.get("salience_operator", {}).get("variant", "diagonal")},
        "temporal_basis": {"variant": temporal_variant},
        "prediction_error_rule": {"variant": learner.get("prediction_error_rule", {}).get("variant", learner.get("algorithm"))},
        "attention_mechanism": {"variant": learner.get("attention_mechanism", {}).get("variant", learner.get("attention", {}).get("mode", "none"))},
        "policy": {"variant": policy.get("name", "null")},
    }


def _extract_attention_summary(payload):
    if not isinstance(payload, dict):
        return None
    experiment = payload.get("experiment")
    if not isinstance(experiment, dict):
        return None
    agent = experiment.get("agent")
    if not isinstance(agent, dict):
        return None
    learning = agent.get("learning")
    if not isinstance(learning, dict):
        return None
    attention = learning.get("attention")
    if not isinstance(attention, dict):
        return None
    initial = attention.get("initial")
    if isinstance(initial, dict):
        return initial
    return None


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
            canonical_payload = to_canonical_payload(payload)
            with open(ctx.report_dir / "payload.json", "w") as f:
                json.dump(canonical_payload, f, indent=2)
            attention = _extract_attention_summary(canonical_payload)
            if isinstance(attention, dict):
                with open(ctx.report_dir / "attention_summary.json", "w") as f:
                    json.dump(attention, f, indent=2)
            mechanism_provenance = _extract_mechanism_provenance(payload)
            if isinstance(mechanism_provenance, dict):
                with open(ctx.report_dir / "mechanism_provenance.json", "w") as f:
                    json.dump(mechanism_provenance, f, indent=2)

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
