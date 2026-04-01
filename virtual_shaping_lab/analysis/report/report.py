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
from virtual_shaping_lab.vsl.rollout.operator_pipeline import OperatorPipeline, default_operator_pipeline
from ui.contracts.report_alignment import (
    ReportAlignmentError,
    build_report_alignment_contract,
    stable_report_alignment_hash,
)

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
    "policy_action": None,
    "policy_available_actions": None,
    "policy_action_scores": None,
    "policy_action_probabilities": None,
    "policy_provenance": None,
    "response": None,
    "reward": None,
    "prediction": None,
    "prediction_error": None,
    "v": None,
    "delta": None,
    "theta": None,
    "attention": None,
    "memory": None,
    "representation": None,
    "context_state": None,
    "generalized_state": None,
    "features": None,
    "observation_provenance": None,
    "protocol_emission": None,
    "protocol_consequence": None,
    "protocol_advance": None,
    "protocol_stop": None,
    "protocol_timing": None,
    "protocol_provenance": None,
    "outcome_type": None,
    "schedule": None,
    "done": None,
    "learning_enabled": None,
    "metadata": {},
}


def _extract_learner_traces(metadata: dict) -> dict[str, object] | None:
    traces = metadata.get("learner_traces")
    if isinstance(traces, dict):
        return traces
    learner = metadata.get("learner")
    if not isinstance(learner, dict):
        return None
    return {
        "v": learner.get("prediction"),
        "delta": learner.get("error"),
        "theta": learner.get("update_features") if isinstance(learner.get("update_features"), dict) else {},
        "attention": learner.get("attention_state") if isinstance(learner.get("attention_state"), dict) else {},
        "memory": learner.get("eligibility_state") if isinstance(learner.get("eligibility_state"), dict) else {},
    }


def _extract_policy_traces(metadata: dict) -> dict[str, object] | None:
    traces = metadata.get("policy_traces")
    if isinstance(traces, dict):
        return traces
    policy = metadata.get("policy")
    if not isinstance(policy, dict):
        return None
    provenance = policy.get("metadata")
    if not isinstance(provenance, dict):
        provenance = {}
    return {
        "action": policy.get("action"),
        "available_actions": list(policy.get("available_actions", []) or []),
        "action_scores": dict(policy.get("action_scores", {}) or {}),
        "action_probabilities": dict(policy.get("action_probabilities", {}) or {}),
        "provenance": dict(provenance),
    }


def _extract_protocol_traces(metadata: dict) -> dict[str, object] | None:
    traces = metadata.get("protocol_traces")
    if isinstance(traces, dict):
        return traces
    protocol = metadata.get("protocol")
    if not isinstance(protocol, dict):
        return None
    return {
        "emission": dict(protocol.get("emission", {}) or {}),
        "consequence": dict(protocol.get("consequence", {}) or {}),
        "advance": dict(protocol.get("advance", {}) or {}),
        "stop": dict(protocol.get("stop", {}) or {}),
        "provenance": {
            "preset_name": protocol.get("preset_name"),
            "pipeline_order": list(protocol.get("pipeline_order", []) or []),
        },
        "timing": {
            "t": dict(protocol.get("advance", {}) or {}).get("t"),
            "phase_step": dict(protocol.get("advance", {}) or {}).get("phase_step"),
            "dt_s": dict(protocol.get("advance", {}) or {}).get("dt_s"),
        },
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
    if isinstance(metadata, dict):
        policy_traces = _extract_policy_traces(metadata)
        if isinstance(policy_traces, dict):
            out["policy_action"] = policy_traces.get("action")
            available_actions = policy_traces.get("available_actions")
            out["policy_available_actions"] = list(available_actions) if isinstance(available_actions, list) else []
            action_scores = policy_traces.get("action_scores")
            out["policy_action_scores"] = dict(action_scores) if isinstance(action_scores, dict) else {}
            action_probabilities = policy_traces.get("action_probabilities")
            out["policy_action_probabilities"] = (
                dict(action_probabilities) if isinstance(action_probabilities, dict) else {}
            )
            provenance = policy_traces.get("provenance")
            out["policy_provenance"] = dict(provenance) if isinstance(provenance, dict) else {}
            if out.get("action") is None:
                out["action"] = out["policy_action"]
            if out.get("policy_state") is None:
                out["policy_state"] = {
                    "action_scores": out["policy_action_scores"],
                    "action_probabilities": out["policy_action_probabilities"],
                }

        learner_traces = _extract_learner_traces(metadata)
        if isinstance(learner_traces, dict):
            out["v"] = learner_traces.get("v")
            out["delta"] = learner_traces.get("delta")
            theta = learner_traces.get("theta")
            out["theta"] = dict(theta) if isinstance(theta, dict) else {}
            attention = learner_traces.get("attention")
            out["attention"] = dict(attention) if isinstance(attention, dict) else {}
            memory = learner_traces.get("memory")
            out["memory"] = dict(memory) if isinstance(memory, dict) else {}
            if out.get("prediction") is None:
                out["prediction"] = out["v"]
            if out.get("prediction_error") is None:
                out["prediction_error"] = out["delta"]
        protocol_traces = _extract_protocol_traces(metadata)
        if isinstance(protocol_traces, dict):
            emission = protocol_traces.get("emission")
            out["protocol_emission"] = dict(emission) if isinstance(emission, dict) else {}
            consequence = protocol_traces.get("consequence")
            out["protocol_consequence"] = dict(consequence) if isinstance(consequence, dict) else {}
            advance = protocol_traces.get("advance")
            out["protocol_advance"] = dict(advance) if isinstance(advance, dict) else {}
            stop = protocol_traces.get("stop")
            out["protocol_stop"] = dict(stop) if isinstance(stop, dict) else {}
            timing = protocol_traces.get("timing")
            out["protocol_timing"] = dict(timing) if isinstance(timing, dict) else {}
            provenance = protocol_traces.get("provenance")
            out["protocol_provenance"] = dict(provenance) if isinstance(provenance, dict) else {}
        observation_traces = metadata.get("observation_traces")
        if isinstance(observation_traces, dict):
            out["representation"] = observation_traces.get("representation")
            out["context_state"] = observation_traces.get("context_state")
            out["generalized_state"] = observation_traces.get("generalized_state")
            features = observation_traces.get("features")
            out["features"] = list(features) if isinstance(features, list) else []
            provenance = observation_traces.get("provenance")
            out["observation_provenance"] = dict(provenance) if isinstance(provenance, dict) else {}
        else:
            observation = metadata.get("observation")
            if isinstance(observation, dict):
                obs_output = observation.get("output")
                if isinstance(obs_output, dict):
                    out["representation"] = obs_output.get("representation")
                    out["context_state"] = obs_output.get("context_state")
                    out["generalized_state"] = obs_output.get("generalized_state")
                    obs_features = obs_output.get("features")
                    out["features"] = list(obs_features) if isinstance(obs_features, list) else []
                    obs_meta = obs_output.get("metadata")
                    out["observation_provenance"] = dict(obs_meta) if isinstance(obs_meta, dict) else {}
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
        "payload_mode_identity": {},
        "basis_compile_identity": {},
        "measurement_provenance_identity": {},
        "tuple_authoring_identity": {},
        "preset_ux_identity": {},
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
            basis_identity = provenance.get("basis_compile_identity")
            if isinstance(basis_identity, dict):
                identity["basis_compile_identity"] = dict(basis_identity)
            payload_mode_identity = provenance.get("payload_mode_identity")
            if isinstance(payload_mode_identity, dict):
                identity["payload_mode_identity"] = dict(payload_mode_identity)
            measurement_identity = provenance.get("measurement_provenance_identity")
            if isinstance(measurement_identity, dict):
                identity["measurement_provenance_identity"] = dict(measurement_identity)
            tuple_identity = provenance.get("tuple_authoring_identity")
            if isinstance(tuple_identity, dict):
                identity["tuple_authoring_identity"] = dict(tuple_identity)
            preset_ux_identity = provenance.get("preset_ux_identity")
            if isinstance(preset_ux_identity, dict):
                identity["preset_ux_identity"] = dict(preset_ux_identity)
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


def _extract_measurement_selection_ids(payload) -> list[str] | None:
    if not isinstance(payload, dict):
        return None
    provenance = payload.get("provenance")
    if not isinstance(provenance, dict):
        return None
    measurement = provenance.get("measurement_provenance_identity")
    if not isinstance(measurement, dict):
        return None
    selection_ids = measurement.get("selection_ids")
    if not isinstance(selection_ids, list):
        return None
    out: list[str] = []
    for item in selection_ids:
        if isinstance(item, str) and item.strip():
            out.append(item)
    return out if out else None


@dataclass(frozen=True)
class ReportRunContext:
    report_dir: Path
    metrics_dir: Path


class ReportArtifactWriter:
    def create_context(self, *, output_dir: str | None = None) -> ReportRunContext:
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        base_dir = Path(output_dir) if output_dir is not None else DEFAULT_REPORTS_DIR
        report_dir = base_dir / timestamp
        suffix = 0
        while report_dir.exists():
            suffix += 1
            report_dir = base_dir / f"{timestamp}_{suffix:02d}"
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

    def write_report_alignment(self, *, alignment: dict | None, ctx: ReportRunContext) -> None:
        if not isinstance(alignment, dict):
            return
        with open(ctx.report_dir / "report_alignment.json", "w") as f:
            json.dump(_to_jsonable(alignment), f, indent=2)
        alignment_hash = stable_report_alignment_hash(alignment)
        with open(ctx.report_dir / "report_alignment_identity.json", "w") as f:
            json.dump(
                {
                    "hash_algorithm": "sha256",
                    "report_alignment_hash": alignment_hash,
                },
                f,
                indent=2,
            )
        with open(ctx.report_dir / "report_alignment.sha256", "w", encoding="utf-8") as f:
            f.write(f"{alignment_hash}\n")


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

    def add_metric_pages(self, *, pdf: ReportPDF, metrics: dict, metric_display_labels: dict[str, str] | None = None) -> None:
        display = metric_display_labels or {}
        for metric_name, metric_result in metrics.items():
            pdf.add_metric_text(display.get(metric_name, metric_name), _to_jsonable(metric_result))

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
    report_alignment = None
    measurement_selection_ids = _extract_measurement_selection_ids(payload)
    strict_readout_coverage = isinstance(measurement_selection_ids, list) and len(measurement_selection_ids) > 0
    try:
        report_alignment = build_report_alignment_contract(
            preset_id=preset,
            metric_names=report_config.metrics,
            measurement_selection_ids=measurement_selection_ids,
            strict_readout_coverage=strict_readout_coverage,
        )
    except (ReportAlignmentError, KeyError):
        if strict_readout_coverage:
            raise
        report_alignment = None
    artifact_writer.write_report_alignment(alignment=report_alignment, ctx=ctx)

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
    metric_display_labels = {}
    if isinstance(report_alignment, dict):
        raw_metric_labels = report_alignment.get("metric_labels")
        if isinstance(raw_metric_labels, dict):
            for metric_name, item in raw_metric_labels.items():
                if isinstance(item, dict) and isinstance(item.get("label"), str) and item["label"].strip():
                    metric_display_labels[str(metric_name)] = item["label"]
    pdf_composer.add_metric_pages(pdf=pdf, metrics=metrics, metric_display_labels=metric_display_labels)
    pdf_composer.close(pdf=pdf)

    return ctx.report_dir
