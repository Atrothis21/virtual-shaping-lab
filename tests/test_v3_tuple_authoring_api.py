from __future__ import annotations

import copy

from api import run as api_run


def test_tuple_guided_catalog_endpoint_shape():
    body = api_run.tuple_authoring_catalog_api()
    assert body["authoring_mode"] == "tuple_v1"
    assert body["registry_generated"] is True
    assert isinstance(body["arrangements"], list) and body["arrangements"]
    assert isinstance(body["tasks"], list) and body["tasks"]
    assert isinstance(body["agents"], list)


def test_tuple_guided_catalog_filters_tasks_and_agents_by_tuple():
    body = api_run.tuple_authoring_catalog_api(arrangement="operant", task="acquisition")
    tasks = {entry["id"]: entry for entry in body["tasks"]}
    assert tasks["acquisition"]["enabled"] is True
    agents = {entry["id"]: entry for entry in body["agents"]}
    assert agents["rw_operant"]["enabled"] is True
    assert agents["rw_classical"]["enabled"] is False


def test_tuple_materialization_smoke_for_pavlovian_and_operant_examples():
    pav = api_run.materialize_tuple_authoring_api(
        {
            "arrangement": "pavlovian",
            "task": "acquisition",
            "agent": "rw_classical",
            "edits": {"n_trials": 12, "cs_plus": ["tone"]},
        }
    )
    assert set(pav["experiment"].keys()) == {"program", "agent", "runtime"}
    assert pav["experiment"]["program"]["phases"][0]["protocol"] == "acquisition"
    assert pav["experiment"]["program"]["phases"][0]["trials"] == 12
    assert pav["tuple_authoring"]["composition_identity"]["task_implementation_id"] == "pavlovian_acquisition"

    oper = api_run.materialize_tuple_authoring_api(
        {
            "arrangement": "operant",
            "task": "acquisition",
            "agent": "rw_operant",
            "edits": {"n_trials": 8, "cs_plus": ["tone"]},
        }
    )
    assert set(oper["experiment"].keys()) == {"program", "agent", "runtime"}
    assert oper["experiment"]["program"]["phases"][0]["trials"] == 8
    assert oper["tuple_authoring"]["composition_identity"]["task_implementation_id"] == "operant_acquisition"


def test_tuple_materialization_legacy_preset_wrapper_parity_smoke():
    legacy_payload = {
        "preset_id": "acquisition",
        "edits": {"n_trials": 9, "cs_plus": ["tone"]},
    }
    tuple_materialized = api_run.materialize_tuple_authoring_api(copy.deepcopy(legacy_payload))
    basis_materialized = api_run.materialize_preset_basis_api(
        "acquisition",
        {
            "operator_subset": {"phi": "elemental", "w": "rescorla_wagner"},
            "edits": {"n_trials": 9, "cs_plus": ["tone"], "learning_rule": "rescorla_wagner"},
        },
    )

    tuple_phase = tuple_materialized["experiment"]["program"]["phases"][0]
    basis_phase = basis_materialized["experiment"]["program"]["phases"][0]
    assert tuple_phase["protocol"] == basis_phase["protocol"] == "acquisition"
    assert tuple_phase["trials"] == basis_phase["trials"] == 9
    assert tuple_phase["stimuli"]["cs_plus"] == basis_phase["stimuli"]["cs_plus"] == ["tone"]

