from pathlib import Path
import json
import hashlib
from typing import Any, Dict, Optional

from api.stores import InMemoryRunStatusStore, RunStatusStoreProtocol
from analysis.public import (
    get_protocol_default_template,
    run_preset_report,
)
from experiment.public import assemble_from_plan, build_plan, run_from_plan
from experiment.domain.types import ExperimentPlan
from experiment.payload_contract import to_canonical_payload
from experiment.basis_routing import BasisAssemblyRoutingError, build_basis_assembly_routing_contract
from virtual_shaping_lab.vsl.rollout.operator_pipeline import OperatorPipeline, default_operator_pipeline
from virtual_shaping_lab.vsl.registry import match_phenomenon_registry_entry_for_protocol
from api.lifecycle import (
    LIFECYCLE_RUN_COMPLETE,
    validate_lifecycle_transition,
)


_DEFAULT_RUN_STATUS_STORE = InMemoryRunStatusStore()

# Backward-compatible symbol for tests/patching; prefer assemble_from_plan.
assemble_experiment = assemble_from_plan
# Backward-compatible symbol for tests/patching; prefer run_preset_report.
run_report = run_preset_report


def _stable_hash_from_artifact_payload(payload: Dict[str, Any], record_schema_version: str) -> str:
    identity = {
        "canonical_payload": {
            "experiment": dict(payload.get("experiment", {}) or {}),
            "report": dict(payload.get("report", {}) or {}),
        },
        "record_schema_version": record_schema_version,
    }
    encoded = json.dumps(identity, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _build_mechanism_provenance(plan: ExperimentPlan) -> Dict[str, Any]:
    runtime_spec = dict(plan.runtime_spec or {})
    composed = runtime_spec.get("composed_parameters")
    if not isinstance(composed, dict):
        return {}

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


def _build_operator_pipeline_identity(plan: ExperimentPlan) -> Dict[str, Any]:
    pipeline = _resolve_operator_pipeline(plan)
    return {
        "stage_keys": list(pipeline.stage_keys()),
        "pipeline_hash": pipeline.stable_hash(),
    }


def _summarize_operator_stage_diagnostics(records: list[dict[str, Any]]) -> Dict[str, Any]:
    """Aggregate stage-level realization diagnostics from emitted records."""
    stage_counts: Dict[str, Dict[str, int]] = {}
    pipeline_hashes: set[str] = set()

    for record in records:
        if not isinstance(record, dict):
            continue
        metadata = record.get("metadata")
        if not isinstance(metadata, dict):
            continue
        op = metadata.get("operator_pipeline")
        if not isinstance(op, dict):
            continue

        pipeline_hash = op.get("pipeline_hash")
        if isinstance(pipeline_hash, str) and pipeline_hash.strip():
            pipeline_hashes.add(pipeline_hash)

        realization = op.get("stage_realization")
        if not isinstance(realization, dict):
            continue
        for stage_key, mode in realization.items():
            stage = str(stage_key)
            mode_key = str(mode)
            if stage not in stage_counts:
                stage_counts[stage] = {"executed": 0, "delegated": 0, "metadata_only": 0}
            if mode_key not in stage_counts[stage]:
                stage_counts[stage][mode_key] = 0
            stage_counts[stage][mode_key] += 1

    return {
        "pipeline_hashes": sorted(pipeline_hashes),
        "realization_matrix": stage_counts,
    }


def _build_basis_compile_identity(plan: ExperimentPlan) -> Dict[str, Any]:
    basis_compile = dict(plan.basis_compile_artifact or {})
    subset_hash = basis_compile.get("frozen_compiled_hash")
    if not isinstance(subset_hash, str) or not subset_hash.strip():
        subset_hash = None

    preset_id = basis_compile.get("preset_id")
    if not isinstance(preset_id, str) or not preset_id.strip():
        preset_id = None

    selected_slots_raw = basis_compile.get("selected_slots")
    selected_slots = (
        [str(slot) for slot in selected_slots_raw if isinstance(slot, str)]
        if isinstance(selected_slots_raw, list)
        else []
    )

    routing_hash = None
    routed_objects: Dict[str, Any] = {}
    try:
        routing_contract = build_basis_assembly_routing_contract(plan)
        routing_hash = routing_contract.get("routing_hash")
        family_routing = routing_contract.get("family_routing")
        if isinstance(family_routing, dict):
            routed_objects = dict(family_routing)
    except BasisAssemblyRoutingError:
        routed_objects = {}

    return {
        "subset_hash": subset_hash,
        "preset_id": preset_id,
        "selected_slots": selected_slots,
        "routing_hash": routing_hash if isinstance(routing_hash, str) and routing_hash else None,
        "routed_objects": routed_objects,
    }


def _build_measurement_provenance_identity(plan: ExperimentPlan) -> Dict[str, Any]:
    basis_compile = dict(plan.basis_compile_artifact or {})
    assembly_spec = basis_compile.get("assembly_spec")
    m_slot = {}
    if isinstance(assembly_spec, dict):
        slots = assembly_spec.get("slots")
        if isinstance(slots, dict):
            raw_m = slots.get("m")
            if isinstance(raw_m, dict):
                m_slot = raw_m

    selection_ids = m_slot.get("selection_ids", []) if isinstance(m_slot.get("selection_ids"), list) else []
    builder_families = (
        m_slot.get("internal_builder_families", [])
        if isinstance(m_slot.get("internal_builder_families"), list)
        else []
    )

    basis_identity = _build_basis_compile_identity(plan)
    report_routes = basis_identity.get("routed_objects", {}).get("report_readout_family", [])
    if not isinstance(report_routes, list):
        report_routes = []

    return {
        "slot": "m",
        "selection_ids": [str(v) for v in selection_ids],
        "internal_builder_families": [str(v) for v in builder_families],
        "report_routes": report_routes,
        "routing_hash": basis_identity.get("routing_hash"),
        "subset_hash": basis_identity.get("subset_hash"),
    }


def _resolve_operator_pipeline(plan: ExperimentPlan) -> OperatorPipeline:
    runtime_spec = dict(plan.runtime_spec or {})
    runtime_settings = runtime_spec.get("runtime")
    raw = None
    if isinstance(runtime_settings, dict):
        raw = runtime_settings.get("operator_pipeline")
    if raw is None:
        raw = runtime_spec.get("operator_pipeline")
    if raw is None and isinstance(plan.canonical_payload, dict):
        experiment = plan.canonical_payload.get("experiment")
        if isinstance(experiment, dict):
            runtime_from_payload = experiment.get("runtime")
            if isinstance(runtime_from_payload, dict):
                raw = runtime_from_payload.get("operator_pipeline")
    pipeline: OperatorPipeline
    if isinstance(raw, OperatorPipeline):
        pipeline = raw
    elif isinstance(raw, dict):
        pipeline = OperatorPipeline.from_dict(raw)
    else:
        pipeline = default_operator_pipeline()
    return pipeline


def _resolve_primary_protocol(plan: ExperimentPlan) -> str:
    if not isinstance(plan.canonical_payload, dict):
        return ""
    experiment = plan.canonical_payload.get("experiment")
    if not isinstance(experiment, dict):
        return ""
    program = experiment.get("program")
    if not isinstance(program, dict):
        return ""
    phases = program.get("phases")
    if not isinstance(phases, list) or not phases:
        return ""
    first = phases[0]
    if not isinstance(first, dict):
        return ""
    return str(first.get("protocol", "") or "").strip()


def _enforce_phenomenon_operator_constraints(plan: ExperimentPlan) -> None:
    protocol = _resolve_primary_protocol(plan)
    entry = match_phenomenon_registry_entry_for_protocol(protocol)
    if entry is None:
        return
    pipeline = _resolve_operator_pipeline(plan)
    declared = set(pipeline.stage_keys())
    required = set(entry.constraints.required_operators)
    missing = sorted(required - declared)
    if missing:
        missing_text = ", ".join(missing)
        declared_text = ", ".join(pipeline.stage_keys())
        raise ValueError(
            f"Operator-constraint violation for phenomenon '{entry.key}' (protocol '{protocol}'): "
            f"missing required operators: {missing_text}. Declared operators: {declared_text}."
        )


def _summarize_learner_spec(spec: Dict[str, Any]) -> Dict[str, Any]:
    metadata = spec.get("metadata", {}) if isinstance(spec.get("metadata"), dict) else {}
    digest = hashlib.sha256(
        json.dumps(spec, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    return {
        "preset_name": metadata.get("preset_name"),
        "spec_hash": digest,
    }


def _build_learner_identity(plan: ExperimentPlan) -> Dict[str, Any]:
    learning = plan.agent_spec.get("learning", {}) if isinstance(plan.agent_spec, dict) else {}
    if isinstance(learning, dict):
        learner_spec = learning.get("learner_spec")
        if isinstance(learner_spec, dict):
            return _summarize_learner_spec(learner_spec)
    settings = plan.settings if isinstance(plan.settings, dict) else {}
    learner_spec = settings.get("learner_spec")
    if isinstance(learner_spec, dict):
        return _summarize_learner_spec(learner_spec)
    return {"preset_name": None, "spec_hash": None}


def _extract_learner_identity_from_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    plan = payload.get("plan")
    if isinstance(plan, dict):
        agent_spec = plan.get("agent_spec")
        if isinstance(agent_spec, dict):
            learning = agent_spec.get("learning", {})
            if isinstance(learning, dict) and isinstance(learning.get("learner_spec"), dict):
                return _summarize_learner_spec(learning.get("learner_spec"))
        settings = plan.get("settings")
        if isinstance(settings, dict) and isinstance(settings.get("learner_spec"), dict):
            return _summarize_learner_spec(settings.get("learner_spec"))
    experiment = payload.get("experiment")
    if isinstance(experiment, dict):
        agent = experiment.get("agent")
        if isinstance(agent, dict):
            learning = agent.get("learning")
            if isinstance(learning, dict) and isinstance(learning.get("learner_spec"), dict):
                return _summarize_learner_spec(learning.get("learner_spec"))
    return {"preset_name": None, "spec_hash": None}


def _artifact_plan_metadata(payload: Dict[str, Any]) -> Dict[str, Any]:
    provenance = payload.get("provenance")
    operator_pipeline_identity = None
    if isinstance(provenance, dict):
        candidate = provenance.get("operator_pipeline")
        if isinstance(candidate, dict):
            operator_pipeline_identity = candidate

    if not isinstance(operator_pipeline_identity, dict):
        runtime = None
        experiment = payload.get("experiment")
        if isinstance(experiment, dict):
            runtime = experiment.get("runtime")
        raw_pipeline = runtime.get("operator_pipeline") if isinstance(runtime, dict) else None
        if isinstance(raw_pipeline, OperatorPipeline):
            operator_pipeline_identity = {
                "stage_keys": list(raw_pipeline.stage_keys()),
                "pipeline_hash": raw_pipeline.stable_hash(),
            }
        elif isinstance(raw_pipeline, dict):
            parsed = OperatorPipeline.from_dict(raw_pipeline)
            operator_pipeline_identity = {
                "stage_keys": list(parsed.stage_keys()),
                "pipeline_hash": parsed.stable_hash(),
            }
        else:
            parsed = default_operator_pipeline()
            operator_pipeline_identity = {
                "stage_keys": list(parsed.stage_keys()),
                "pipeline_hash": parsed.stable_hash(),
            }

    plan_data = payload.get("plan")
    if isinstance(plan_data, dict):
        record_schema_version = str(plan_data.get("record_schema_version", "v1"))
        seed_identity = plan_data.get("seed")
        canonical_payload = plan_data.get("canonical_payload")
        if isinstance(canonical_payload, dict):
            plan_hash = _stable_hash_from_artifact_payload(
                {
                    "experiment": dict(canonical_payload.get("experiment", payload.get("experiment", {})) or {}),
                    "report": dict(canonical_payload.get("report", payload.get("report", {})) or {}),
                },
                record_schema_version,
            )
        else:
            plan_hash = _stable_hash_from_artifact_payload(payload, record_schema_version)
        return {
            "plan_hash": plan_hash,
            "record_schema_version": record_schema_version,
            "seed_identity": seed_identity,
            "operator_pipeline_identity": operator_pipeline_identity,
            "learner_identity": _extract_learner_identity_from_payload(payload),
            "basis_compile_identity": (
                dict(provenance.get("basis_compile_identity", {}))
                if isinstance(provenance, dict) and isinstance(provenance.get("basis_compile_identity"), dict)
                else {}
            ),
            "measurement_provenance_identity": (
                dict(provenance.get("measurement_provenance_identity", {}))
                if isinstance(provenance, dict) and isinstance(provenance.get("measurement_provenance_identity"), dict)
                else {}
            ),
        }

    record_schema_version = "v1"
    seed_identity = None
    experiment = payload.get("experiment")
    if isinstance(experiment, dict):
        program = experiment.get("program")
        if isinstance(program, dict):
            phases = program.get("phases")
            if isinstance(phases, list) and phases:
                first = phases[0]
                if isinstance(first, dict):
                    params = first.get("params")
                    if isinstance(params, dict):
                        seed_identity = params.get("rng_seed")
    return {
        "plan_hash": _stable_hash_from_artifact_payload(payload, record_schema_version),
        "record_schema_version": record_schema_version,
        "seed_identity": seed_identity,
        "operator_pipeline_identity": operator_pipeline_identity,
        "learner_identity": _extract_learner_identity_from_payload(payload),
        "basis_compile_identity": (
            dict(provenance.get("basis_compile_identity", {}))
            if isinstance(provenance, dict) and isinstance(provenance.get("basis_compile_identity"), dict)
            else {}
        ),
        "measurement_provenance_identity": (
            dict(provenance.get("measurement_provenance_identity", {}))
            if isinstance(provenance, dict) and isinstance(provenance.get("measurement_provenance_identity"), dict)
            else {}
        ),
    }


def _fallback_plan_metadata_from_status(*, run_id: str, source_status: Dict[str, Any]) -> Dict[str, Any]:
    metadata = source_status.get("metadata") if isinstance(source_status.get("metadata"), dict) else {}
    record_schema_version = str(metadata.get("record_schema_version", "v1"))
    plan_hash = metadata.get("plan_hash")
    if not isinstance(plan_hash, str) or not plan_hash.strip():
        encoded = json.dumps(
            {"source_run_id": run_id, "record_schema_version": record_schema_version},
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        plan_hash = hashlib.sha256(encoded).hexdigest()

    operator_pipeline_identity = metadata.get("operator_pipeline_identity")
    if not isinstance(operator_pipeline_identity, dict):
        pipeline = default_operator_pipeline()
        operator_pipeline_identity = {
            "stage_keys": list(pipeline.stage_keys()),
            "pipeline_hash": pipeline.stable_hash(),
        }

    learner_identity = metadata.get("learner_identity")
    if not isinstance(learner_identity, dict):
        learner_identity = {"preset_name": None, "spec_hash": None}

    return {
        "plan_hash": plan_hash,
        "record_schema_version": record_schema_version,
        "seed_identity": metadata.get("seed_identity"),
        "operator_pipeline_identity": operator_pipeline_identity,
        "learner_identity": learner_identity,
        "basis_compile_identity": (
            dict(metadata.get("basis_compile_identity", {}))
            if isinstance(metadata.get("basis_compile_identity"), dict)
            else {}
        ),
        "measurement_provenance_identity": (
            dict(metadata.get("measurement_provenance_identity", {}))
            if isinstance(metadata.get("measurement_provenance_identity"), dict)
            else {}
        ),
    }


def _set_status_with_lifecycle(
    store: RunStatusStoreProtocol,
    run_id: str,
    *,
    state: str,
    artifacts: Optional[Dict[str, Any]] = None,
    metadata: Optional[Dict[str, Any]] = None,
    error: Optional[Dict[str, Any]] = None,
) -> None:
    previous = store.get(run_id) or {}
    prev_meta = dict(previous.get("metadata", {}))
    previous_lifecycle_state = previous.get("lifecycle_state") or prev_meta.get("lifecycle_state")
    lifecycle_state = LIFECYCLE_RUN_COMPLETE if state == "completed" else state
    validate_lifecycle_transition(previous_lifecycle_state, lifecycle_state)
    merged_meta = dict(metadata or {})
    merged_meta["lifecycle_state"] = lifecycle_state
    store.set(
        run_id,
        state=state,
        artifacts=artifacts or {},
        metadata=merged_meta,
        error=error,
    )


class RunStatusStore:
    """
    Backward-compatible facade over the default run status store.

    New code should inject RunStatusStoreProtocol into services.
    """

    @classmethod
    def set(
        cls,
        run_id: str,
        *,
        state: str,
        artifacts: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        error: Optional[Dict[str, Any]] = None,
    ) -> None:
        _set_status_with_lifecycle(
            _DEFAULT_RUN_STATUS_STORE,
            run_id,
            state=state,
            artifacts=artifacts,
            metadata=metadata,
            error=error,
        )

    @classmethod
    def get(cls, run_id: str) -> Optional[Dict[str, Any]]:
        data = _DEFAULT_RUN_STATUS_STORE.get(run_id)
        if data is None:
            return None
        out = dict(data)
        metadata = dict(out.get("metadata", {}))
        lifecycle_state = metadata.pop("lifecycle_state", None)
        if lifecycle_state is not None:
            out["lifecycle_state"] = lifecycle_state
        out["metadata"] = metadata
        return out

    @classmethod
    def clear(cls, run_id: Optional[str] = None) -> None:
        _DEFAULT_RUN_STATUS_STORE.clear(run_id)


class PlanService:
    """Application-layer facade for payload -> resolved plan operations."""

    @staticmethod
    def resolve(payload: Dict[str, Any]) -> Dict[str, Any]:
        plan = build_plan(payload)
        _enforce_phenomenon_operator_constraints(plan)
        return {
            "plan": plan.to_dict(),
            "stable_hash": plan.stable_hash(),
        }


class RunService:
    """Application-layer facade for plan execution and run-status tracking."""

    @staticmethod
    def _build_report_payload_from_plan(plan: ExperimentPlan) -> Dict[str, Any]:
        payload = to_canonical_payload(
            {
                "experiment": dict(plan.canonical_payload.get("experiment", {}) or {}),
                "report": dict(plan.canonical_payload.get("report", {}) or {}),
            }
        )
        if not payload.get("report"):
            payload["report"] = {"preset": "verification_report"}
        payload["provenance"] = {
            "mechanisms": _build_mechanism_provenance(plan),
            "operator_pipeline": _build_operator_pipeline_identity(plan),
            "basis_compile_identity": _build_basis_compile_identity(plan),
            "measurement_provenance_identity": _build_measurement_provenance_identity(plan),
        }
        payload["plan"] = plan.to_dict()
        return payload

    @staticmethod
    def _run_experiment(*, plan: ExperimentPlan, reports_dir: Path):
        # Compatibility hook: allows API-contract tests to patch assembly seam.
        assemble_experiment(plan)
        execution = run_from_plan(plan)

        records = []
        units = list(plan.units or [])
        for phase_index, phase_records in enumerate(execution.unit_records):

            phase_name = f"Phase {phase_index}"
            if phase_index < len(units):
                unit = units[phase_index]
                if isinstance(unit, dict):
                    phase_name = str(unit.get("name", phase_name))

            for record in phase_records:
                record["phase"] = phase_index
                from experiment.runtime_records import finalize_record

                finalize_record(
                    record,
                    phase_name=phase_name,
                )

            records.extend(phase_records)

        report_preset = str((plan.analysis_spec or {}).get("report_preset", "verification_report"))
        report_payload = RunService._build_report_payload_from_plan(plan)
        report_dir = run_report(
            records=records,
            preset=report_preset,
            payload=report_payload,
            output_dir=str(reports_dir),
        )

        report_dir = Path(report_dir)
        artifacts = {
            "pdf": str(report_dir / "report.pdf"),
            "figures": [str(p) for p in report_dir.glob("*.png")],
            "provenance": str(report_dir / "mechanism_provenance.json"),
            "artifact_identity": str(report_dir / "artifact_identity.json"),
        }
        return records, report_dir, artifacts

    @classmethod
    def execute(
        cls,
        payload: Dict[str, Any],
        *,
        reports_dir: Path,
        expected_plan_hash: Optional[str] = None,
        status_store: Optional[RunStatusStoreProtocol] = None,
    ) -> Dict[str, Any]:
        store = status_store or _DEFAULT_RUN_STATUS_STORE
        plan = build_plan(payload)
        _enforce_phenomenon_operator_constraints(plan)
        plan_hash = plan.stable_hash()
        if expected_plan_hash is not None and expected_plan_hash != plan_hash:
            raise ValueError(
                f"Plan hash mismatch: expected '{expected_plan_hash}', got '{plan_hash}'."
            )

        records, report_dir, artifacts = cls._run_experiment(plan=plan, reports_dir=reports_dir)
        run_id = report_dir.name
        run_metadata = {
            "plan_hash": plan_hash,
            "record_schema_version": plan.record_schema_version,
            "template_version_used": 1,
            "seed_identity": plan.seed,
            "mechanism_provenance": _build_mechanism_provenance(plan),
            "operator_pipeline_identity": _build_operator_pipeline_identity(plan),
            "learner_identity": _build_learner_identity(plan),
            "basis_compile_identity": _build_basis_compile_identity(plan),
            "measurement_provenance_identity": _build_measurement_provenance_identity(plan),
            "operator_stage_diagnostics": _summarize_operator_stage_diagnostics(records),
        }
        _set_status_with_lifecycle(
            store,
            run_id,
            state="completed",
            artifacts=artifacts,
            metadata=run_metadata,
            error=None,
        )
        return {
            "run_id": run_id,
            "artifacts": artifacts,
            "metadata": run_metadata,
            "state": "completed",
            "record_count": len(records),
        }

    @staticmethod
    def status(run_id: str, *, status_store: Optional[RunStatusStoreProtocol] = None) -> Optional[Dict[str, Any]]:
        store = status_store or _DEFAULT_RUN_STATUS_STORE
        data = store.get(run_id)
        if data is None:
            return None
        out = dict(data)
        metadata = dict(out.get("metadata", {}))
        lifecycle_state = metadata.pop("lifecycle_state", None)
        if lifecycle_state is not None:
            out["lifecycle_state"] = lifecycle_state
        out["metadata"] = metadata
        return out


class ReportService:
    """Application-layer facade for report generation from prior runs."""

    @classmethod
    def create_default(
        cls,
        run_id: str,
        *,
        reports_dir: Path,
        preset_override: Optional[str] = None,
        status_store: Optional[RunStatusStoreProtocol] = None,
    ) -> Dict[str, Any]:
        store = status_store or _DEFAULT_RUN_STATUS_STORE
        run_dir = Path(reports_dir) / run_id
        records_path = run_dir / "records.json"
        payload_path = run_dir / "payload.json"
        source_status = store.get(run_id) or {}
        source_metadata = dict(source_status.get("metadata", {}))

        if not records_path.exists():
            raise FileNotFoundError(f"Run artifacts for '{run_id}' not found.")

        with records_path.open("r", encoding="utf-8") as f:
            records = json.load(f)
        payload: Dict[str, Any] | None = None
        if payload_path.exists():
            with payload_path.open("r", encoding="utf-8") as f:
                raw_payload = json.load(f)
            payload = to_canonical_payload(raw_payload)
            if isinstance(raw_payload, dict):
                if isinstance(raw_payload.get("provenance"), dict):
                    payload["provenance"] = dict(raw_payload["provenance"])
                if isinstance(raw_payload.get("plan"), dict):
                    payload["plan"] = dict(raw_payload["plan"])

        preset = preset_override
        if not preset and isinstance(payload, dict):
            preset = payload.get("report", {}).get("preset")
        if not preset:
            preset = "acquisition"

        plan_meta = _artifact_plan_metadata(payload) if isinstance(payload, dict) else _fallback_plan_metadata_from_status(
            run_id=run_id,
            source_status=source_status,
        )
        protocol_name = ""
        if isinstance(payload, dict) and isinstance(payload.get("experiment"), dict):
            exp = payload["experiment"]
            program = exp.get("program")
            if isinstance(program, dict):
                phases = program.get("phases")
                if isinstance(phases, list) and phases:
                    protocol_name = str(phases[0].get("protocol", "") or "")
        if protocol_name:
            template_version = get_protocol_default_template(protocol_name).template_version
        else:
            template_version = int(source_metadata.get("template_version_used", 1) or 1)

        regen_root = Path(reports_dir) / "regenerated"
        regen_root.mkdir(parents=True, exist_ok=True)
        report_dir = run_report(
            records=records,
            preset=preset,
            payload=payload,
            output_dir=str(regen_root),
        )
        report_dir = Path(report_dir)
        artifacts = {
            "pdf": str(report_dir / "report.pdf"),
            "figures": [str(p) for p in report_dir.glob("*.png")],
            "artifact_identity": str(report_dir / "artifact_identity.json"),
        }
        required_source_keys = {"plan_hash", "record_schema_version", "template_version_used"}
        missing_source_keys = sorted([k for k in required_source_keys if k not in source_metadata])
        source_metadata_complete = len(missing_source_keys) == 0
        regeneration_mode = "from_artifacts" if isinstance(payload, dict) else "from_records"
        plan_basis_identity = plan_meta.get("basis_compile_identity")
        source_basis_identity = source_metadata.get("basis_compile_identity")
        basis_compile_identity = (
            plan_basis_identity
            if isinstance(plan_basis_identity, dict) and plan_basis_identity
            else (source_basis_identity if isinstance(source_basis_identity, dict) else {})
        )
        plan_measure_identity = plan_meta.get("measurement_provenance_identity")
        source_measure_identity = source_metadata.get("measurement_provenance_identity")
        measurement_provenance_identity = (
            plan_measure_identity
            if isinstance(plan_measure_identity, dict) and plan_measure_identity
            else (source_measure_identity if isinstance(source_measure_identity, dict) else {})
        )

        new_run_id = report_dir.name
        _set_status_with_lifecycle(
            store,
            new_run_id,
            state="completed",
            artifacts=artifacts,
            metadata={
                "plan_hash": plan_meta["plan_hash"],
                "record_schema_version": plan_meta["record_schema_version"],
                "template_version_used": template_version,
                "seed_identity": plan_meta["seed_identity"],
                "mechanism_provenance": (
                    payload.get("provenance", {}).get("mechanisms", {})
                    if isinstance(payload, dict)
                    else source_metadata.get("mechanism_provenance", {})
                ),
                "operator_pipeline_identity": plan_meta.get("operator_pipeline_identity"),
                "learner_identity": (
                    plan_meta.get("learner_identity")
                    if isinstance(plan_meta.get("learner_identity"), dict)
                    else {"preset_name": None, "spec_hash": None}
                ),
                "basis_compile_identity": basis_compile_identity,
                "measurement_provenance_identity": measurement_provenance_identity,
                "operator_stage_diagnostics": (
                    source_metadata.get("operator_stage_diagnostics", {})
                    if isinstance(source_metadata.get("operator_stage_diagnostics"), dict)
                    else {}
                ),
                "source_run_id": run_id,
                "source_metadata_complete": source_metadata_complete,
                "missing_source_metadata": missing_source_keys,
                "regeneration_mode": regeneration_mode,
            },
            error=None,
        )
        return {
            "run_id": new_run_id,
            "artifacts": artifacts,
            "metadata": {
                "source_run_id": run_id,
                "preset": preset,
                "regenerated": True,
                "plan_hash": plan_meta["plan_hash"],
                "record_schema_version": plan_meta["record_schema_version"],
                "template_version_used": template_version,
                "seed_identity": plan_meta["seed_identity"],
                "mechanism_provenance": (
                    payload.get("provenance", {}).get("mechanisms", {})
                    if isinstance(payload, dict)
                    else source_metadata.get("mechanism_provenance", {})
                ),
                "operator_pipeline_identity": plan_meta.get("operator_pipeline_identity"),
                "learner_identity": (
                    plan_meta.get("learner_identity")
                    if isinstance(plan_meta.get("learner_identity"), dict)
                    else {"preset_name": None, "spec_hash": None}
                ),
                "basis_compile_identity": basis_compile_identity,
                "measurement_provenance_identity": measurement_provenance_identity,
                "operator_stage_diagnostics": (
                    source_metadata.get("operator_stage_diagnostics", {})
                    if isinstance(source_metadata.get("operator_stage_diagnostics"), dict)
                    else {}
                ),
                "source_metadata_complete": source_metadata_complete,
                "missing_source_metadata": missing_source_keys,
                "regeneration_mode": regeneration_mode,
            },
        }
