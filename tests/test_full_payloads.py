from pathlib import Path

from analysis.report.report import run_report
from experiment.assemble import assemble_experiment
from experiment.config import ExperimentConfig
from experiment.runner import Runner
from experiment.runtime_records import finalize_record
from ui.validate_payload import validate_payload

from tests.preset_payloads import PRESET_PAYLOADS


def _run_full_payload(payload: dict, output_dir: Path) -> None:
    validate_payload(payload)
    config = ExperimentConfig.from_payload(payload)
    protocols, agent, representation = assemble_experiment(config)

    records = []
    for phase_index, protocol in enumerate(protocols):
        runner = Runner(protocol)
        phase_records = runner.run()
        for r in phase_records:
            r["phase"] = phase_index
            finalize_record(r, phase_name=config.phases[phase_index].name)
        records.extend(phase_records)

    run_report(
        records=records,
        preset=config.report_preset,
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
