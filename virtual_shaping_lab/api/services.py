from pathlib import Path
import json
from typing import Any, Dict, Optional

from analysis.report.report import run_report
from experiment.assemble import assemble_experiment
from experiment.config import ExperimentConfig
from experiment.runner import Runner


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
        error: Optional[Dict[str, Any]] = None,
    ) -> None:
        cls._runs[run_id] = {
            "state": state,
            "artifacts": artifacts or {},
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
    def _run_experiment(raw_payload: dict, *, reports_dir: Path):
        config = ExperimentConfig.from_payload(raw_payload)
        protocols, _agent, _representation = assemble_experiment(config)

        records = []
        for phase_index, protocol in enumerate(protocols):
            runner = Runner(protocol)
            phase_records = runner.run()

            for record in phase_records:
                record["phase"] = phase_index
                from experiment.runtime_records import finalize_record

                finalize_record(
                    record,
                    phase_name=config.phases[phase_index].name,
                )

            records.extend(phase_records)

        report_dir = run_report(
            records=records,
            preset=config.report_preset,
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
    def execute(cls, payload: Dict[str, Any], *, reports_dir: Path) -> Dict[str, Any]:
        records, report_dir, artifacts = cls._run_experiment(payload, reports_dir=reports_dir)
        run_id = report_dir.name
        RunStatusStore.set(
            run_id,
            state="completed",
            artifacts=artifacts,
            error=None,
        )
        return {
            "run_id": run_id,
            "artifacts": artifacts,
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
            error=None,
        )
        return {
            "run_id": new_run_id,
            "artifacts": artifacts,
            "metadata": {
                "source_run_id": run_id,
                "preset": preset,
                "regenerated": True,
            },
        }
