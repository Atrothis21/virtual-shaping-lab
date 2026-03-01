import copy

import pytest

from api.contracts import (
    ErrorEnvelope,
    PlanResolveResponse,
    ReportCreateResponse,
    RunCreateResponse,
    RunStatusResponse,
)
from analysis.report.report import run_report as real_run_report
from api import run as api_run
from api.services import PlanService
from preset_payloads import CONTRACT_FIXTURES


def test_api_response_dto_required_fields_smoke():
    run_create = RunCreateResponse(status="success", run_id="r1", artifacts={"pdf": "p"}).to_dict()
    assert set(("status", "run_id", "artifacts")).issubset(run_create.keys())

    run_status = RunStatusResponse(status="success", run_id="r1", state="completed").to_dict()
    assert set(("status", "run_id", "state", "artifacts", "error")).issubset(run_status.keys())

    plan_resolve = PlanResolveResponse(status="success", plan={"units": []}, stable_hash="abc").to_dict()
    assert set(("status", "plan", "stable_hash")).issubset(plan_resolve.keys())

    report_create = ReportCreateResponse(status="success", run_id="r1", artifacts={"pdf": "p"}).to_dict()
    assert set(("status", "run_id", "artifacts")).issubset(report_create.keys())

    error = ErrorEnvelope(code="validation_error", message="bad payload").to_dict()
    assert set(("code", "message", "details")).issubset(error.keys())


@pytest.mark.parametrize(
    "fixture_name",
    ["classical_preset", "operant_preset", "multi_phase_builder"],
)
def test_plan_api_contract_fixtures(fixture_name):
    payload = copy.deepcopy(CONTRACT_FIXTURES[fixture_name])
    body = api_run.plan_api(payload)
    assert body.get("status") == "success"
    assert isinstance(body.get("plan"), dict)
    assert isinstance(body.get("stable_hash"), str) and body["stable_hash"]


def test_plan_service_returns_stable_hash_parity():
    from experiment.domain.types import ExperimentPlan

    payload = copy.deepcopy(CONTRACT_FIXTURES["classical_preset"])
    resolved = PlanService.resolve(payload)
    assert "plan" in resolved and isinstance(resolved["plan"], dict)
    assert "stable_hash" in resolved and isinstance(resolved["stable_hash"], str)
    rebuilt = ExperimentPlan.from_dict(resolved["plan"])
    assert resolved["stable_hash"] == rebuilt.stable_hash()


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
    assert "artifacts" in body and isinstance(body["artifacts"], dict)

    run_dir = fixture_output_dir / run_id
    assert run_dir.exists()
    assert (run_dir / "payload.json").exists()
    assert (run_dir / "records.json").exists()
