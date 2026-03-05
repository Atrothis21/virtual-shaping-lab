from pathlib import Path

from analysis.public import run_preset_report
from experiment.config import ExperimentConfig
from experiment.domain.types import ExperimentPlan
from experiment.public import run_from_plan
from ui.validate_payload import validate_payload

import sys

sys.path.append(str(Path(__file__).resolve().parent))
from preset_payloads import PRESET_PAYLOADS


def _run_full_payload(payload: dict, output_dir: Path) -> None:
    validate_payload(payload)
    plan = ExperimentConfig.plan_from_payload(payload)
    assert isinstance(plan, ExperimentPlan)
    execution = run_from_plan(plan)

    run_preset_report(
        # Public facade remains the only analysis entrypoint for this integration test.
        records=execution.records,
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
