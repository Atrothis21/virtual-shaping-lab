from pathlib import Path

from analysis.report.report import run_report
from experiment.assemble import assemble_experiment
from experiment.config import ExperimentConfig
from experiment.domain.types import ExperimentPlan
from experiment.runner import Runner
from experiment.runtime_records import finalize_record
from ui.validate_payload import validate_payload

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent))
from preset_payloads import PRESET_PAYLOADS


def _run_full_payload(payload: dict, output_dir: Path) -> None:
    validate_payload(payload)
    plan = ExperimentConfig.plan_from_payload(payload)
    assert isinstance(plan, ExperimentPlan)
    protocols, agent, representation = assemble_experiment(plan)

    records = []
    plan_units = list(plan.units or [])
    for phase_index, protocol in enumerate(protocols):
        runner = Runner(protocol, settings=dict(plan.settings or {}))
        phase_records = runner.run()
        phase_name = f"Phase {phase_index}"
        if phase_index < len(plan_units) and isinstance(plan_units[phase_index], dict):
            phase_name = str(plan_units[phase_index].get("name", phase_name))
        for r in phase_records:
            r["phase"] = phase_index
            finalize_record(r, phase_name=phase_name)
        records.extend(phase_records)

    run_report(
        records=records,
        preset=str((plan.settings or {}).get("report_preset", "verification_report")),
        payload=payload,
        output_dir=str(output_dir),
    )


def test_full_payloads(tmp_path):
    for name, payload in PRESET_PAYLOADS:
        out_dir = tmp_path / name
        out_dir.mkdir(parents=True, exist_ok=True)
        try:
            _run_full_payload(payload, out_dir)
        except Exception as exc:
            raise AssertionError(f"Full payload failed for preset: {name}") from exc
