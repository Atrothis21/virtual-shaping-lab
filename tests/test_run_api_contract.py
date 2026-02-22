import copy

import pytest

from analysis.report.report import run_report as real_run_report
from api import run as api_run
from preset_payloads import CONTRACT_FIXTURES


@pytest.mark.parametrize(
    "fixture_name",
    ["classical_preset", "operant_preset", "multi_phase_builder"],
)
def test_run_api_contract_fixtures(monkeypatch, tmp_path, fixture_name):
    payload = copy.deepcopy(CONTRACT_FIXTURES[fixture_name])
    fixture_output_dir = tmp_path / fixture_name
    fixture_output_dir.mkdir(parents=True, exist_ok=True)

    def _run_report_to_tmp(records, preset, payload=None, output_dir="reports"):
        return real_run_report(
            records=records,
            preset=preset,
            payload=payload,
            output_dir=str(fixture_output_dir),
        )

    monkeypatch.setattr(api_run, "run_report", _run_report_to_tmp)

    body = api_run.run_api(payload)
    assert body.get("status") == "success"
    run_id = body.get("run_id")
    assert isinstance(run_id, str) and run_id

    run_dir = fixture_output_dir / run_id
    assert run_dir.exists()
    assert (run_dir / "payload.json").exists()
    assert (run_dir / "records.json").exists()
