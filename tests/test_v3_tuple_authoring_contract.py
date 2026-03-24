from __future__ import annotations

import copy

import pytest

from ui.contracts.tuple_authoring_contract import (
    TUPLE_AUTHORING_CONTRACT_VERSION,
    TUPLE_AUTHORING_MODE,
    TupleAuthoringContractError,
    translate_to_tuple_authoring_payload,
    validate_tuple_authoring_payload,
)


def test_tuple_authoring_payload_schema_accepts_valid_tuple():
    payload = {
        "contract_version": TUPLE_AUTHORING_CONTRACT_VERSION,
        "authoring_mode": TUPLE_AUTHORING_MODE,
        "arrangement": "pavlovian",
        "task": "acquisition",
        "agent": "rw_classical",
        "edits": {"n_trials": 25},
    }
    validated = validate_tuple_authoring_payload(payload)
    assert validated["arrangement"] == "pavlovian"
    assert validated["task"] == "acquisition"
    assert validated["agent"] == "rw_classical"


def test_tuple_authoring_payload_rejects_malformed_tuple():
    payload = {
        "arrangement": "pavlovian",
        "task": "acquisition",
        "agent": "rw_classical",
        "edits": [],
    }
    with pytest.raises(TupleAuthoringContractError, match="tuple_authoring.edits must be an object"):
        validate_tuple_authoring_payload(payload)


def test_tuple_authoring_payload_rejects_arrangement_agent_mismatch():
    payload = {
        "arrangement": "pavlovian",
        "task": "acquisition",
        "agent": "rw_operant",
        "edits": {},
    }
    with pytest.raises(TupleAuthoringContractError, match="not compatible with arrangement"):
        validate_tuple_authoring_payload(payload)


def test_legacy_preset_translation_to_tuple_has_diagnostics():
    legacy = {
        "preset_id": "acquisition",
        "operator_subset": {"phi": "elemental", "w": "rescorla_wagner"},
        "edits": {"n_trials": 10},
    }
    translated = translate_to_tuple_authoring_payload(copy.deepcopy(legacy))
    out = translated["translated_payload"]
    diagnostics = translated["diagnostics"]
    assert out["arrangement"] == "pavlovian"
    assert out["task"] == "acquisition"
    assert out["agent"] == "rw_classical"
    assert diagnostics["legacy_preset_label"] == "Acquisition"
    assert diagnostics["translation_quality"] == "heuristic"
    assert diagnostics["deprecation_diagnostics"]
    assert diagnostics["translated_tuple"]["task"] == "acquisition"


def test_tuple_payload_pass_through_translation_reports_lossless():
    payload = {
        "arrangement": "operant",
        "task": "acquisition",
        "agent": "rw_operant",
        "edits": {"epsilon": 0.1},
    }
    translated = translate_to_tuple_authoring_payload(payload)
    assert translated["translated_payload"]["authoring_mode"] == TUPLE_AUTHORING_MODE
    assert translated["diagnostics"]["translation_quality"] == "lossless"
    assert translated["diagnostics"]["legacy_preset_label"] is None


def test_translation_rejects_payload_without_tuple_or_legacy_keys():
    with pytest.raises(TupleAuthoringContractError, match="must include tuple keys"):
        translate_to_tuple_authoring_payload({"edits": {}})

