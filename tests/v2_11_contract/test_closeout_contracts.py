import copy
import json

import pytest

from analysis.public import run_preset_report as real_run_report
from api import run as api_run
from api import services as api_services
from experiment.domain.types import ExperimentPlan
from experiment.public import build_plan
from preset_payloads import CONTRACT_FIXTURES


def _classical_payload():
    return copy.deepcopy(CONTRACT_FIXTURES["classical_preset"])


def test_public_build_plan_exposes_typed_envelope_and_canonical_payload():
    plan = build_plan(_classical_payload())

    assert isinstance(plan, ExperimentPlan)
    assert isinstance(plan.program_spec, dict) and plan.program_spec["phases"]
    assert isinstance(plan.agent_spec, dict) and "learning" in plan.agent_spec
    assert isinstance(plan.runtime_spec, dict)
    assert set(plan.canonical_payload.keys()) == {"experiment", "report"}
    assert set(plan.canonical_payload["experiment"].keys()) == {"program", "agent", "runtime"}
    assert plan.canonical_payload["experiment"]["program"]["phases"][0]["protocol"] == "acquisition"
    assert plan.canonical_payload["experiment"]["agent"]["learning"]["rule"] == "rescorla_wagner"


def test_public_build_plan_rejects_legacy_payload_shape():
    with pytest.raises(ValueError, match="Legacy payload shape is no longer accepted at runtime"):
        build_plan(
            {
                "experiment": {
                    "learner": "rescorla_wagner",
                    "agent": "classical_agent",
                    "phases": [{"name": "Acq", "protocol": "acquisition", "params": {"n_trials": 1}}],
                },
                "report": {"preset": "acquisition"},
            }
        )


def test_public_build_plan_rejects_phase_param_ownership_leaks():
    payload = _classical_payload()
    payload["experiment"]["program"]["phases"][0]["params"]["attention"] = {"tone": 0.8}

    with pytest.raises(ValueError, match="must not include representation/learner-owned keys"):
        build_plan(payload)


def test_run_contract_emits_minimum_record_schema_and_artifact_identity(monkeypatch, tmp_path):
    payload = _classical_payload()
    fixture_output_dir = tmp_path / "closeout_contract_fixture"
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
    run_dir = fixture_output_dir / body["run_id"]

    records = json.loads((run_dir / "records.json").read_text(encoding="utf-8"))
    assert records, "run must persist at least one record"
    for field in ("step", "trial", "tick", "stimulus", "action", "reward", "prediction", "prediction_error", "policy_state"):
        assert field in records[0], f"minimum record schema missing '{field}'"

    artifact_identity = json.loads((run_dir / "artifact_identity.json").read_text(encoding="utf-8"))
    assert isinstance(artifact_identity.get("engine_version"), str) and artifact_identity["engine_version"]
    assert artifact_identity.get("record_schema_version") == "v1"
    assert artifact_identity.get("plan_hash") == body["metadata"]["plan_hash"]
    assert artifact_identity.get("seed_identity") == body["metadata"]["seed_identity"]
    assert isinstance(artifact_identity.get("mechanism_identity"), dict)

    provenance = json.loads((run_dir / "mechanism_provenance.json").read_text(encoding="utf-8"))
    assert isinstance(provenance, dict)
    assert isinstance(body["metadata"].get("mechanism_provenance"), dict)
