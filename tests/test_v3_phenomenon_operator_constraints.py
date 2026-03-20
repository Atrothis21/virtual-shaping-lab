from __future__ import annotations

import copy

import pytest

from api import services as api_services
from tests.preset_payloads import CONTRACT_FIXTURES, blocking_payload
from virtual_shaping_lab.vsl.operator import default_operator_pipeline


def _pipeline_without(stage_key: str) -> dict:
    payload = default_operator_pipeline().to_dict()
    payload["stages"] = [stage for stage in payload["stages"] if stage.get("key") != stage_key]
    return payload


def test_v3_slice3_plan_service_rejects_missing_required_operator_for_registered_protocol():
    payload = copy.deepcopy(blocking_payload())
    payload["experiment"]["runtime"]["operator_pipeline"] = _pipeline_without("Err")

    with pytest.raises(ValueError, match="Operator-constraint violation"):
        api_services.PlanService.resolve(payload)


def test_v3_slice3_run_service_rejects_missing_required_operator_for_registered_protocol(tmp_path):
    payload = copy.deepcopy(blocking_payload())
    payload["experiment"]["runtime"]["operator_pipeline"] = _pipeline_without("Err")

    with pytest.raises(ValueError, match="Operator-constraint violation"):
        api_services.RunService.execute(payload, reports_dir=tmp_path)


def test_v3_slice3_unregistered_protocol_is_not_gated_by_phenomenon_constraints():
    payload = copy.deepcopy(CONTRACT_FIXTURES["classical_preset"])
    payload["experiment"]["runtime"]["operator_pipeline"] = _pipeline_without("Err")

    resolved = api_services.PlanService.resolve(payload)
    assert isinstance(resolved.get("stable_hash"), str) and resolved["stable_hash"]

