from pathlib import Path
import json
from typing import Any, Dict, Optional

from api.stores import InMemoryRunStatusStore, RunStatusStoreProtocol
from analysis.public import (
    get_protocol_default_template,
    run_preset_report,
)
from experiment.public import assemble_from_plan, build_plan, run_from_plan
from experiment.domain.types import ExperimentPlan
from experiment.payload_contract import to_canonical_payload
from api.lifecycle import (
    LIFECYCLE_RUN_COMPLETE,
    validate_lifecycle_transition,
)


_DEFAULT_RUN_STATUS_STORE = InMemoryRunStatusStore()

# Backward-compatible symbol for tests/patching; prefer assemble_from_plan.
assemble_experiment = assemble_from_plan
# Backward-compatible symbol for tests/patching; prefer run_preset_report.
run_report = run_preset_report


def _build_mechanism_provenance(plan: ExperimentPlan) -> Dict[str, Any]:
    settings = dict(plan.settings or {})
    composed = settings.get("composed_parameters")
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
        return {
            "plan": plan.to_dict(),
            "stable_hash": plan.stable_hash(),
        }


class RunService:
    """Application-layer facade for plan execution and run-status tracking."""

    @staticmethod
    @staticmethod
    def _build_report_payload_from_plan(plan: ExperimentPlan) -> Dict[str, Any]:
        settings = dict(plan.settings or {})
        units = list(plan.units or [])
        phases: list[Dict[str, Any]] = []
        for i, unit in enumerate(units):
            if isinstance(unit, dict):
                params = unit.get("params") or {}
                trials = params.get("n_trials")
                if trials is None:
                    trials = 1
                phases.append(
                    {
                        "name": unit.get("name", f"Phase {i}"),
                        "protocol": unit.get("protocol"),
                        "stimuli": unit.get("stimuli"),
                        "params": params,
                        "trials": int(trials),
                    }
                )
        runtime = (
            ((settings.get("composed_parameters") or {}).get("runtime") or {})
            if isinstance(settings.get("composed_parameters"), dict)
            else {}
        )
        runtime = dict(runtime) if isinstance(runtime, dict) else {}
        if isinstance(settings.get("context_inference"), dict):
            runtime.setdefault("context_inference", dict(settings.get("context_inference", {})))

        return {
            "experiment": {
                "program": {
                    "phases": phases,
                },
                "agent": {
                    "name": settings.get("agent"),
                    "representation": settings.get("representation"),
                    "learning": {
                        "rule": settings.get("learner"),
                        "params": {},
                        "attention": {
                            "config": settings.get("attention_config", {}),
                            "initial": settings.get("attention", {}),
                        },
                    },
                    "policy": settings.get("policy"),
                },
                "runtime": runtime,
            },
            "report": {
                "preset": settings.get("report_preset", "verification_report"),
            },
            "provenance": {
                "mechanisms": _build_mechanism_provenance(plan),
            },
            "plan": plan.to_dict(),
        }

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

        report_preset = str((plan.settings or {}).get("report_preset", "verification_report"))
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
            "mechanism_provenance": _build_mechanism_provenance(plan),
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

        if not records_path.exists() or not payload_path.exists():
            raise FileNotFoundError(f"Run artifacts for '{run_id}' not found.")

        with records_path.open("r", encoding="utf-8") as f:
            records = json.load(f)
        with payload_path.open("r", encoding="utf-8") as f:
            payload = to_canonical_payload(json.load(f))

        preset = preset_override or payload.get("report", {}).get("preset")
        if not preset:
            preset = "acquisition"

        resolved_plan = build_plan(payload)
        protocol_name = ""
        if isinstance(payload.get("experiment"), dict):
            exp = payload["experiment"]
            program = exp.get("program")
            if isinstance(program, dict):
                phases = program.get("phases")
                if isinstance(phases, list) and phases:
                    protocol_name = str(phases[0].get("protocol", "") or "")
        template_version = get_protocol_default_template(protocol_name).template_version if protocol_name else 1

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
        }
        source_status = store.get(run_id) or {}
        source_metadata = dict(source_status.get("metadata", {}))
        required_source_keys = {"plan_hash", "record_schema_version", "template_version_used"}
        missing_source_keys = sorted([k for k in required_source_keys if k not in source_metadata])
        source_metadata_complete = len(missing_source_keys) == 0

        new_run_id = report_dir.name
        _set_status_with_lifecycle(
            store,
            new_run_id,
            state="completed",
            artifacts=artifacts,
            metadata={
                "plan_hash": resolved_plan.stable_hash(),
                "record_schema_version": resolved_plan.record_schema_version,
                "template_version_used": template_version,
                "mechanism_provenance": _build_mechanism_provenance(resolved_plan),
                "source_run_id": run_id,
                "source_metadata_complete": source_metadata_complete,
                "missing_source_metadata": missing_source_keys,
                "regeneration_mode": "from_artifacts",
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
                "plan_hash": resolved_plan.stable_hash(),
                "record_schema_version": resolved_plan.record_schema_version,
                "template_version_used": template_version,
                "mechanism_provenance": _build_mechanism_provenance(resolved_plan),
                "source_metadata_complete": source_metadata_complete,
                "missing_source_metadata": missing_source_keys,
                "regeneration_mode": "from_artifacts",
            },
        }
