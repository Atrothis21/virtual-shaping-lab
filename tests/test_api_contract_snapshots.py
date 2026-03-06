from __future__ import annotations

import copy
import json
from pathlib import Path

from analysis.public import run_preset_report as real_run_report
from api import run as api_run
from api import services as api_services
from preset_payloads import CONTRACT_FIXTURES


def _load_snapshots() -> dict:
    path = Path(__file__).resolve().parent / "fixtures" / "api_contract_snapshots.json"
    return json.loads(path.read_text(encoding="utf-8"))


def _assert_exact_keys(data: dict, expected_keys: list[str]) -> None:
    assert set(data.keys()) == set(expected_keys)


def test_plan_endpoint_snapshot_shape():
    snapshots = _load_snapshots()
    expected = snapshots["plan"]

    payload = copy.deepcopy(CONTRACT_FIXTURES["classical_preset"])
    body = api_run.plan_api(payload)

    _assert_exact_keys(body, expected["top_level_keys"])
    assert set(expected["plan_required_keys"]).issubset(set(body["plan"].keys()))
    _assert_exact_keys(body["lifecycle"], expected["lifecycle_keys"])


def test_run_and_status_endpoint_snapshot_shape(monkeypatch, tmp_path):
    snapshots = _load_snapshots()
    expected_run = snapshots["run"]
    expected_status = snapshots["run_status"]

    payload = copy.deepcopy(CONTRACT_FIXTURES["classical_preset"])
    fixture_output_dir = tmp_path / "run_snapshot_fixture"
    fixture_output_dir.mkdir(parents=True, exist_ok=True)

    def _run_report_to_tmp(records, preset, payload=None, output_dir="reports"):
        return real_run_report(
            records=records,
            preset=preset,
            payload=payload,
            output_dir=str(fixture_output_dir),
        )

    monkeypatch.setattr(api_services, "run_report", _run_report_to_tmp)

    run_body = api_run.run_api(payload)
    _assert_exact_keys(run_body, expected_run["top_level_keys"])
    assert set(expected_run["metadata_required_keys"]).issubset(set(run_body["metadata"].keys()))
    _assert_exact_keys(run_body["lifecycle"], expected_run["lifecycle_keys"])

    status_body = api_run.run_status_api(run_body["run_id"])
    _assert_exact_keys(status_body, expected_status["top_level_keys"])
    assert set(expected_status["metadata_required_keys"]).issubset(set(status_body["metadata"].keys()))
    _assert_exact_keys(status_body["lifecycle"], expected_status["lifecycle_keys"])


def test_report_endpoint_snapshot_shape(monkeypatch, tmp_path):
    snapshots = _load_snapshots()
    expected = snapshots["report"]

    payload = copy.deepcopy(CONTRACT_FIXTURES["classical_preset"])
    fixture_output_dir = tmp_path / "report_snapshot_fixture"
    fixture_output_dir.mkdir(parents=True, exist_ok=True)

    def _run_report_to_tmp(records, preset, payload=None, output_dir="reports"):
        return real_run_report(
            records=records,
            preset=preset,
            payload=payload,
            output_dir=str(output_dir),
        )

    monkeypatch.setattr(api_run, "reports_dir", fixture_output_dir)
    monkeypatch.setattr(api_services, "run_report", _run_report_to_tmp)

    run_body = api_run.run_api(payload)
    report_body = api_run.run_report_api(run_body["run_id"])

    _assert_exact_keys(report_body, expected["top_level_keys"])
    assert set(expected["metadata_required_keys"]).issubset(set(report_body["metadata"].keys()))
    _assert_exact_keys(report_body["lifecycle"], expected["lifecycle_keys"])


def test_extensions_endpoint_snapshot_shape():
    snapshots = _load_snapshots()
    expected = snapshots["extensions"]

    body = api_run.extensions_api()
    _assert_exact_keys(body, expected["top_level_keys"])
    _assert_exact_keys(body["extensions"], expected["extensions_keys"])
    _assert_exact_keys(body["versions"], expected["versions_keys"])

