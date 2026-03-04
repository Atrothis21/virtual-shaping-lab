import copy

import pytest
from fastapi import HTTPException

from api.contracts import (
    ErrorEnvelope,
    PlanResolveResponse,
    ReportCreateResponse,
    RunCreateResponse,
    RunStatusResponse,
)
from analysis.report.report import run_report as real_run_report
from api import run as api_run
from api import services as api_services
from api.services import PlanService
from preset_payloads import CONTRACT_FIXTURES


def test_api_response_dto_required_fields_smoke():
    run_create = RunCreateResponse(
        status="success",
        run_id="r1",
        state="completed",
        artifacts={"pdf": "p"},
        metadata={"plan_hash": "abc", "record_schema_version": "v1", "template_version_used": 1},
    ).to_dict()
    assert set(("status", "run_id", "state", "artifacts", "metadata", "lifecycle")).issubset(run_create.keys())

    run_status = RunStatusResponse(status="success", run_id="r1", state="completed").to_dict()
    assert set(("status", "run_id", "state", "artifacts", "metadata", "error", "lifecycle")).issubset(run_status.keys())

    plan_resolve = PlanResolveResponse(status="success", plan={"units": []}, stable_hash="abc").to_dict()
    assert set(("status", "plan", "stable_hash", "lifecycle")).issubset(plan_resolve.keys())

    report_create = ReportCreateResponse(
        status="success",
        run_id="r1",
        artifacts={"pdf": "p"},
        metadata={"preset": "acquisition"},
    ).to_dict()
    assert set(("status", "run_id", "artifacts", "metadata", "lifecycle")).issubset(report_create.keys())

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
    assert body["lifecycle"]["state"] == "PlanResolved"
    assert "create_run" in body["lifecycle"]["next_actions"]


def test_plan_service_returns_stable_hash_parity():
    from experiment.domain.types import ExperimentPlan

    payload = copy.deepcopy(CONTRACT_FIXTURES["classical_preset"])
    resolved = PlanService.resolve(payload)
    assert "plan" in resolved and isinstance(resolved["plan"], dict)
    assert "stable_hash" in resolved and isinstance(resolved["stable_hash"], str)
    rebuilt = ExperimentPlan.from_dict(resolved["plan"])
    assert resolved["stable_hash"] == rebuilt.stable_hash()


def test_run_service_rejects_expected_plan_hash_mismatch(tmp_path):
    payload = copy.deepcopy(CONTRACT_FIXTURES["classical_preset"])
    with pytest.raises(ValueError, match="Plan hash mismatch"):
        api_services.RunService.execute(
            payload,
            reports_dir=tmp_path,
            expected_plan_hash="deadbeef",
        )


def test_run_api_forwards_expected_plan_hash_and_rejects_mismatch():
    payload = copy.deepcopy(CONTRACT_FIXTURES["classical_preset"])
    payload["expected_plan_hash"] = "deadbeef"
    with pytest.raises(HTTPException) as exc:
        api_run.run_api(payload)
    assert exc.value.status_code == 400
    assert exc.value.detail["code"] == "validation_error"
    assert "Plan hash mismatch" in str(exc.value.detail.get("message", ""))
    assert "Plan hash mismatch" in str(exc.value.detail.get("details", {}).get("reason", ""))


def test_run_service_executes_from_resolved_plan(monkeypatch, tmp_path):
    from experiment import assemble as assemble_mod
    from experiment.domain.types import ExperimentPlan

    payload = copy.deepcopy(CONTRACT_FIXTURES["classical_preset"])
    calls = {"saw_plan": False}

    def _assemble_assert_plan(config):
        assert isinstance(config, ExperimentPlan)
        calls["saw_plan"] = True
        return assemble_mod.assemble_experiment(config)

    def _run_report_to_tmp(records, preset, payload=None, output_dir="reports"):
        return real_run_report(
            records=records,
            preset=preset,
            payload=payload,
            output_dir=str(tmp_path),
        )

    monkeypatch.setattr(api_services, "assemble_experiment", _assemble_assert_plan)
    monkeypatch.setattr(api_services, "run_report", _run_report_to_tmp)
    result = api_services.RunService.execute(payload, reports_dir=tmp_path)

    assert calls["saw_plan"] is True
    assert result["state"] == "completed"


def test_run_service_supports_injected_status_store(monkeypatch, tmp_path):
    payload = copy.deepcopy(CONTRACT_FIXTURES["classical_preset"])

    class DummyStore:
        def __init__(self):
            self.data = {}

        def set(self, run_id, *, state, artifacts=None, metadata=None, error=None):
            self.data[run_id] = {
                "state": state,
                "artifacts": artifacts or {},
                "metadata": metadata or {},
                "error": error,
            }

        def get(self, run_id):
            return self.data.get(run_id)

        def clear(self, run_id=None):
            if run_id is None:
                self.data.clear()
                return
            self.data.pop(run_id, None)

    store = DummyStore()

    def _run_report_to_tmp(records, preset, payload=None, output_dir="reports"):
        return real_run_report(
            records=records,
            preset=preset,
            payload=payload,
            output_dir=str(tmp_path),
        )

    monkeypatch.setattr(api_services, "run_report", _run_report_to_tmp)
    result = api_services.RunService.execute(payload, reports_dir=tmp_path, status_store=store)
    status = api_services.RunService.status(result["run_id"], status_store=store)

    assert result["run_id"] in store.data
    assert status is not None
    assert status["state"] == "completed"


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

    monkeypatch.setattr(api_services, "run_report", _run_report_to_tmp)

    body = api_run.run_api(payload)
    assert body.get("status") == "success"
    run_id = body.get("run_id")
    assert isinstance(run_id, str) and run_id
    assert body.get("state") == "completed"
    assert "artifacts" in body and isinstance(body["artifacts"], dict)
    assert "metadata" in body and isinstance(body["metadata"], dict)
    assert isinstance(body["metadata"].get("plan_hash"), str) and body["metadata"]["plan_hash"]
    assert body["metadata"].get("record_schema_version") == "v1"
    assert isinstance(body["metadata"].get("template_version_used"), int)
    assert body["lifecycle"]["state"] == "RunComplete"
    assert "create_report" in body["lifecycle"]["next_actions"]

    run_dir = fixture_output_dir / run_id
    assert run_dir.exists()
    assert (run_dir / "payload.json").exists()
    assert (run_dir / "records.json").exists()


def test_run_status_endpoint_returns_completed(monkeypatch, tmp_path):
    payload = copy.deepcopy(CONTRACT_FIXTURES["classical_preset"])
    fixture_output_dir = tmp_path / "status_fixture"
    fixture_output_dir.mkdir(parents=True, exist_ok=True)

    def _run_report_to_tmp(records, preset, payload=None, output_dir="reports"):
        return real_run_report(
            records=records,
            preset=preset,
            payload=payload,
            output_dir=str(fixture_output_dir),
        )

    monkeypatch.setattr(api_services, "run_report", _run_report_to_tmp)

    body = api_run.run_api(payload)
    run_id = body["run_id"]
    status = api_run.run_status_api(run_id)
    assert status["status"] == "success"
    assert status["run_id"] == run_id
    assert status["state"] == "completed"
    assert isinstance(status["metadata"].get("plan_hash"), str) and status["metadata"]["plan_hash"]
    assert status["metadata"].get("record_schema_version") == "v1"
    assert isinstance(status["metadata"].get("template_version_used"), int)
    assert status["lifecycle"]["state"] == "RunComplete"
    assert "create_report" in status["lifecycle"]["next_actions"]


def test_run_status_endpoint_404_for_missing_run():
    with pytest.raises(HTTPException) as exc:
        api_run.run_status_api("missing-run-id")
    assert exc.value.status_code == 404
    assert exc.value.detail["code"] == "not_found"
    assert "message" in exc.value.detail
    assert "details" in exc.value.detail


def test_run_report_endpoint_regenerates_report(monkeypatch, tmp_path):
    payload = copy.deepcopy(CONTRACT_FIXTURES["classical_preset"])
    fixture_output_dir = tmp_path / "report_regen_fixture"
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
    source_run_id = run_body["run_id"]

    report_body = api_run.run_report_api(source_run_id)
    assert report_body["status"] == "success"
    assert isinstance(report_body["run_id"], str) and report_body["run_id"]
    assert isinstance(report_body["artifacts"], dict)
    assert report_body["metadata"]["source_run_id"] == source_run_id
    assert report_body["metadata"]["regenerated"] is True
    assert isinstance(report_body["metadata"].get("plan_hash"), str) and report_body["metadata"]["plan_hash"]
    assert report_body["metadata"].get("record_schema_version") == "v1"
    assert isinstance(report_body["metadata"].get("template_version_used"), int)
    assert report_body["metadata"]["regeneration_mode"] == "from_artifacts"
    assert report_body["metadata"]["source_metadata_complete"] is True
    assert report_body["metadata"]["missing_source_metadata"] == []
    assert report_body["lifecycle"]["state"] == "ReportComplete"
    assert "view_report" in report_body["lifecycle"]["next_actions"]


def test_run_report_endpoint_flags_missing_source_metadata(monkeypatch, tmp_path):
    payload = copy.deepcopy(CONTRACT_FIXTURES["classical_preset"])
    fixture_output_dir = tmp_path / "report_regen_missing_meta_fixture"
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
    source_run_id = run_body["run_id"]

    # Simulate legacy/degraded source status metadata.
    api_services.RunStatusStore.set(
        source_run_id,
        state="completed",
        artifacts=run_body["artifacts"],
        metadata={"plan_hash": "abc"},
        error=None,
    )

    report_body = api_run.run_report_api(source_run_id)
    assert report_body["metadata"]["regeneration_mode"] == "from_artifacts"
    assert report_body["metadata"]["source_metadata_complete"] is False
    assert set(report_body["metadata"]["missing_source_metadata"]) == {
        "record_schema_version",
        "template_version_used",
    }


def test_run_report_endpoint_404_for_missing_run():
    with pytest.raises(HTTPException) as exc:
        api_run.run_report_api("missing-run-id")
    assert exc.value.status_code == 404
    assert exc.value.detail["code"] == "not_found"
    assert "message" in exc.value.detail
    assert "details" in exc.value.detail


def test_plan_api_validation_error_envelope():
    with pytest.raises(HTTPException) as exc:
        api_run.plan_api({"report": {"preset": "acquisition"}})
    assert exc.value.status_code == 400
    assert exc.value.detail["code"] == "validation_error"
    assert "message" in exc.value.detail
    assert "details" in exc.value.detail


def test_plan_api_internal_error_envelope(monkeypatch):
    monkeypatch.setattr(api_run, "validate_payload", lambda _: None)

    def _boom(_):
        raise RuntimeError("boom")

    monkeypatch.setattr(api_services.PlanService, "resolve", _boom)
    with pytest.raises(HTTPException) as exc:
        api_run.plan_api({"experiment": {}, "report": {}})
    assert exc.value.status_code == 500
    assert exc.value.detail["code"] == "internal_error"
    assert "message" in exc.value.detail
    assert "details" in exc.value.detail


def test_extensions_api_contract_shape():
    body = api_run.extensions_api()
    assert body["status"] == "success"
    ext = body["extensions"]
    assert set(ext.keys()) == {
        "protocols",
        "learners",
        "policies",
        "representations",
        "report_templates",
    }
    assert isinstance(ext["protocols"], list)
    assert isinstance(ext["learners"], list)
    assert isinstance(ext["policies"], list)
    assert isinstance(ext["representations"], list)
    assert isinstance(ext["report_templates"], dict)
