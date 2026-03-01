from pathlib import Path
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
