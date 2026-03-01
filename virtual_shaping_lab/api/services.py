from pathlib import Path
import json
from typing import Any, Dict, Optional

from analysis.report.catalog import get_default_template_for_protocol
from analysis.report.report import run_report
from experiment.assemble import assemble_experiment
from experiment.config import ExperimentConfig
from experiment.domain.types import ExperimentPlan
from experiment.runner import Runner
from api.lifecycle import (
    LIFECYCLE_RUN_COMPLETE,
    validate_lifecycle_transition,
)


class RunStatusStore:
    """In-process run status registry."""

    _runs: Dict[str, Dict[str, Any]] = {}

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
        previous = cls._runs.get(run_id, {})
        previous_lifecycle_state = previous.get("lifecycle_state")
        lifecycle_state = LIFECYCLE_RUN_COMPLETE if state == "completed" else state
        validate_lifecycle_transition(previous_lifecycle_state, lifecycle_state)
        cls._runs[run_id] = {
            "state": state,
            "lifecycle_state": lifecycle_state,
            "artifacts": artifacts or {},
            "metadata": metadata or {},
            "error": error,
        }

    @classmethod
    def get(cls, run_id: str) -> Optional[Dict[str, Any]]:
        return cls._runs.get(run_id)


class PlanService:
    """Application-layer facade for payload -> resolved plan operations."""

    @staticmethod
    def resolve(payload: Dict[str, Any]) -> Dict[str, Any]:
        plan = ExperimentConfig.plan_from_payload(payload)
        return {
            "plan": plan.to_dict(),
            "stable_hash": plan.stable_hash(),
        }


class RunService:
    """Application-layer facade for plan execution and run-status tracking."""

    @staticmethod
    def _run_experiment(raw_payload: dict, *, plan: ExperimentPlan, reports_dir: Path):
        protocols, _agent, _representation = assemble_experiment(plan)

        records = []
        units = list(plan.units or [])
        for phase_index, protocol in enumerate(protocols):
            runner = Runner(protocol)
            phase_records = runner.run()

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
        report_dir = run_report(
            records=records,
            preset=report_preset,
            payload=raw_payload,
            output_dir=str(reports_dir),
        )

        report_dir = Path(report_dir)
        artifacts = {
            "pdf": str(report_dir / "report.pdf"),
            "figures": [str(p) for p in report_dir.glob("*.png")],
        }
        return records, report_dir, artifacts

    @classmethod
    def execute(
        cls,
        payload: Dict[str, Any],
        *,
        reports_dir: Path,
        expected_plan_hash: Optional[str] = None,
    ) -> Dict[str, Any]:
        plan = ExperimentConfig.plan_from_payload(payload)
        plan_hash = plan.stable_hash()
        if expected_plan_hash is not None and expected_plan_hash != plan_hash:
            raise ValueError(
                f"Plan hash mismatch: expected '{expected_plan_hash}', got '{plan_hash}'."
            )

        records, report_dir, artifacts = cls._run_experiment(
            payload,
            plan=plan,
            reports_dir=reports_dir,
        )
        run_id = report_dir.name
        run_metadata = {
            "plan_hash": plan_hash,
            "record_schema_version": plan.record_schema_version,
            "template_version_used": 1,
        }
        RunStatusStore.set(
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
    def status(run_id: str) -> Optional[Dict[str, Any]]:
        return RunStatusStore.get(run_id)


class ReportService:
    """Application-layer facade for report generation from prior runs."""

    @classmethod
    def create_default(
        cls,
        run_id: str,
        *,
        reports_dir: Path,
        preset_override: Optional[str] = None,
    ) -> Dict[str, Any]:
        run_dir = Path(reports_dir) / run_id
        records_path = run_dir / "records.json"
        payload_path = run_dir / "payload.json"

        if not records_path.exists() or not payload_path.exists():
            raise FileNotFoundError(f"Run artifacts for '{run_id}' not found.")

        with records_path.open("r", encoding="utf-8") as f:
            records = json.load(f)
        with payload_path.open("r", encoding="utf-8") as f:
            payload = json.load(f)

        preset = preset_override or payload.get("report", {}).get("preset")
        if not preset:
            preset = "acquisition"

        resolved_plan = ExperimentConfig.plan_from_payload(payload)
        protocol_name = ""
        if isinstance(payload.get("experiment"), dict):
            exp = payload["experiment"]
            if isinstance(exp.get("phases"), list) and exp["phases"]:
                protocol_name = str(exp["phases"][0].get("protocol", "") or "")
            else:
                protocol_name = str(exp.get("protocol", "") or "")
        template_version = get_default_template_for_protocol(protocol_name).template_version if protocol_name else 1

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
        new_run_id = report_dir.name
        RunStatusStore.set(
            new_run_id,
            state="completed",
            artifacts=artifacts,
            metadata={
                "plan_hash": resolved_plan.stable_hash(),
                "record_schema_version": resolved_plan.record_schema_version,
                "template_version_used": template_version,
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
            },
        }
