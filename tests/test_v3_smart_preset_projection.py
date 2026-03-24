from __future__ import annotations

import copy

import pytest

from api import run as api_run
from ui.contracts.smart_preset_projection import (
    SMART_PRESET_PROJECTIONS,
    SmartPresetProjectionValidationError,
    get_smart_preset_projection_contract,
    list_smart_preset_ids,
    project_smart_preset_to_tuple_payload,
    validate_smart_preset_projection_contract,
)
from ui.contracts.tuple_authoring_api import materialize_tuple_authoring_payload


def test_smart_preset_projection_contract_shape_and_catalog_endpoint():
    payload = get_smart_preset_projection_contract()
    assert isinstance(payload["version"], str) and payload["version"]
    assert isinstance(payload["smart_presets"], dict) and payload["smart_presets"]

    body = api_run.smart_preset_catalog_api()
    assert body["registry_generated"] is True
    assert body["contract_version"] == payload["version"]
    assert isinstance(body["smart_presets"], list) and body["smart_presets"]


def test_smart_preset_projection_parity_with_tuple_materialization():
    projected = project_smart_preset_to_tuple_payload(
        "classical_acquisition",
        edits={"n_trials": 11, "cs_plus": ["tone"]},
    )
    direct = {
        "arrangement": "pavlovian",
        "task": "acquisition",
        "agent": "rw_classical",
        "edits": {"n_trials": 11, "cs_plus": ["tone"]},
    }
    projected_materialized = materialize_tuple_authoring_payload(projected)
    direct_materialized = materialize_tuple_authoring_payload(direct)

    projected_phase = projected_materialized["experiment"]["program"]["phases"][0]
    direct_phase = direct_materialized["experiment"]["program"]["phases"][0]
    assert projected_phase["protocol"] == direct_phase["protocol"] == "acquisition"
    assert projected_phase["trials"] == direct_phase["trials"] == 11
    assert projected_phase["stimuli"]["cs_plus"] == direct_phase["stimuli"]["cs_plus"] == ["tone"]
    assert (
        projected_materialized["tuple_authoring"]["composition_identity"]["composition_hash"]
        == direct_materialized["tuple_authoring"]["composition_identity"]["composition_hash"]
    )


def test_smart_preset_projection_rejects_duplicated_operator_payload_definition():
    payload = copy.deepcopy(SMART_PRESET_PROJECTIONS)
    first_id = next(iter(payload["smart_presets"].keys()))
    payload["smart_presets"][first_id]["operator_subset"] = {"phi": "elemental"}
    with pytest.raises(SmartPresetProjectionValidationError, match="cannot define 'operator_subset'"):
        validate_smart_preset_projection_contract(payload)


def test_smart_preset_projection_rejects_hidden_defaults_layer():
    payload = copy.deepcopy(SMART_PRESET_PROJECTIONS)
    first_id = next(iter(payload["smart_presets"].keys()))
    payload["smart_presets"][first_id]["hidden_defaults"] = {"n_trials": 999}
    with pytest.raises(SmartPresetProjectionValidationError, match="cannot define 'hidden_defaults'"):
        validate_smart_preset_projection_contract(payload)


def test_smart_preset_projection_defaults_to_empty_edits_object():
    for smart_preset_id in list_smart_preset_ids():
        projected = project_smart_preset_to_tuple_payload(smart_preset_id)
        assert projected["edits"] == {}
