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
from virtual_shaping_lab.vsl.operator import OperatorPipeline, default_operator_pipeline

DEFAULT_REPORTS_DIR = REPORTS_DIR
_VERSION_FILE = Path(__file__).resolve().parents[3] / "VERSION"


def _to_jsonable(value):
    if isinstance(value, dict):
        return {str(k): _to_jsonable(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_to_jsonable(v) for v in value]
    if isinstance(value, tuple):
        return [_to_jsonable(v) for v in value]
    return value


_ANALYSIS_RECORD_DEFAULTS = {
    "phase": None,
    "phase_name": None,
    "protocol_name": None,
    "unit_path": None,
    "subphase": None,
    "subphase_name": None,
    "trial": None,
    "step": None,
    "tick": None,
    "t_s": None,
    "dt_s": None,
    "trial_step": None,
    "trial_id": None,
    "context": None,
    "stimulus": None,
    "stimulus_type": None,
    "action": None,
    "policy_state": None,
    "response": None,
    "reward": None,
    "prediction": None,
    "prediction_error": None,
    "outcome_type": None,
    "schedule": None,
    "done": None,
    "learning_enabled": None,
    "metadata": {},
}


def _normalize_record_for_artifact(record):
    out = dict(record)
    for key, default in _ANALYSIS_RECORD_DEFAULTS.items():
        if key not in out:
            out[key] = {} if key == "metadata" else default
    if out.get("step") is None:
        out["step"] = out.get("trial_step")
        if out.get("step") is None:
            out["step"] = out.get("tick")
    debug = out.get("debug")
    if out.get("prediction_error") is None and isinstance(debug, dict):
        out["prediction_error"] = debug.get("prediction_error")
    metadata = out.get("metadata")
    if out.get("policy_state") is None and isinstance(metadata, dict):
        candidate = metadata.get("policy_state")
        if isinstance(candidate, dict):
            out["policy_state"] = dict(candidate)
    return out


def _load_engine_version() -> str:
    try:
        return _VERSION_FILE.read_text(encoding="utf-8").strip()
    except OSError:
        return "unknown"


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


def _extract_learner_identity(payload):
    if not isinstance(payload, dict):
        return {"preset_name": None, "spec_hash": None}

    plan = payload.get("plan")
    learner_spec = None
    if isinstance(plan, dict):
        agent_spec = plan.get("agent_spec")
        if isinstance(agent_spec, dict):
            learning = agent_spec.get("learning")
            if isinstance(learning, dict) and isinstance(learning.get("learner_spec"), dict):
                learner_spec = dict(learning["learner_spec"])
        if learner_spec is None:
            settings = plan.get("settings")
            if isinstance(settings, dict) and isinstance(settings.get("learner_spec"), dict):
                learner_spec = dict(settings["learner_spec"])

    if learner_spec is None:
        experiment = payload.get("experiment")
        if isinstance(experiment, dict):
            agent = experiment.get("agent")
            if isinstance(agent, dict):
                learning = agent.get("learning")
                if isinstance(learning, dict) and isinstance(learning.get("learner_spec"), dict):
                    learner_spec = dict(learning["learner_spec"])

    if not isinstance(learner_spec, dict):
        return {"preset_name": None, "spec_hash": None}

    digest = json.dumps(learner_spec, sort_keys=True, separators=(",", ":")).encode("utf-8")
    metadata = learner_spec.get("metadata", {}) if isinstance(learner_spec.get("metadata"), dict) else {}
    import hashlib

    return {
        "preset_name": metadata.get("preset_name"),
        "spec_hash": hashlib.sha256(digest).hexdigest(),
    }


def _extract_artifact_identity(payload):
    identity = {
        "engine_version": _load_engine_version(),
        "record_schema_version": "v1",
        "plan_hash": None,
        "seed_identity": None,
        "mechanism_identity": None,
        "operator_pipeline_identity": None,
        "learner_identity": _extract_learner_identity(payload),
    }

    mechanism_provenance = _extract_mechanism_provenance(payload)
    if isinstance(mechanism_provenance, dict):
        identity["mechanism_identity"] = mechanism_provenance

    if isinstance(payload, dict):
        provenance = payload.get("provenance")
        if isinstance(provenance, dict):
            operator_pipeline = provenance.get("operator_pipeline")
            if isinstance(operator_pipeline, dict):
                identity["operator_pipeline_identity"] = {
                    "stage_keys": list(operator_pipeline.get("stage_keys", []) or []),
                    "pipeline_hash": operator_pipeline.get("pipeline_hash"),
                }
        if identity["operator_pipeline_identity"] is None:
            experiment = payload.get("experiment")
            runtime = experiment.get("runtime") if isinstance(experiment, dict) else None
            raw = runtime.get("operator_pipeline") if isinstance(runtime, dict) else None
            if isinstance(raw, OperatorPipeline):
                identity["operator_pipeline_identity"] = {
                    "stage_keys": list(raw.stage_keys()),
                    "pipeline_hash": raw.stable_hash(),
                }
            elif isinstance(raw, dict):
                parsed = OperatorPipeline.from_dict(raw)
                identity["operator_pipeline_identity"] = {
                    "stage_keys": list(parsed.stage_keys()),
                    "pipeline_hash": parsed.stable_hash(),
                }
            else:
                parsed = default_operator_pipeline()
                identity["operator_pipeline_identity"] = {
                    "stage_keys": list(parsed.stage_keys()),
                    "pipeline_hash": parsed.stable_hash(),
                }

    if not isinstance(payload, dict):
        return identity

    plan = payload.get("plan")
    if isinstance(plan, dict):
        if plan.get("record_schema_version"):
            identity["record_schema_version"] = str(plan.get("record_schema_version"))
        if plan.get("seed") is not None:
            identity["seed_identity"] = plan.get("seed")
        canonical_payload = plan.get("canonical_payload")
        if isinstance(canonical_payload, dict):
            identity_payload = {
                "canonical_payload": canonical_payload,
                "record_schema_version": identity["record_schema_version"],
            }
            import hashlib

            encoded = json.dumps(identity_payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
            identity["plan_hash"] = hashlib.sha256(encoded).hexdigest()

    experiment = payload.get("experiment")
    if identity["seed_identity"] is None and isinstance(experiment, dict):
        program = experiment.get("program")
        if isinstance(program, dict):
            phases = program.get("phases")
            if isinstance(phases, list) and phases:
                first = phases[0]
                if isinstance(first, dict):
                    params = first.get("params")
                    if isinstance(params, dict) and params.get("rng_seed") is not None:
                        identity["seed_identity"] = params.get("rng_seed")

    return identity


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
        normalized_records = [_normalize_record_for_artifact(record) for record in records]
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
            with open(ctx.report_dir / "artifact_identity.json", "w") as f:
                json.dump(_extract_artifact_identity(payload), f, indent=2)

        with open(ctx.report_dir / "records.json", "w") as f:
            json.dump(normalized_records, f, indent=2)

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
