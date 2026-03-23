from __future__ import annotations

import copy

import pytest

from ui.contracts.dependent_variable_registry import DEPENDENT_VARIABLE_REGISTRY
from ui.contracts.operator_graph_backlinks import (
    OperatorGraphBacklinkError,
    list_operator_graph_backlinks,
    resolve_operator_graph_backlinks,
    validate_operator_graph_backlink_integrity_from_payloads,
    validate_operator_graph_backlink_integrity,
)
from ui.contracts.operator_registry import OPERATOR_REGISTRY
from ui.contracts.trialstate_registry import TRIALSTATE_FIELD_REGISTRY


def test_operator_graph_backlinks_resolve_for_prediction_error_operator():
    backlinks = resolve_operator_graph_backlinks("delta")
    assert backlinks["operator"]["id"] == "delta"
    assert backlinks["graph_backlinks"]
    variable_ids = {item["id"] for item in backlinks["graph_backlinks"]}
    assert "prediction_error" in variable_ids
    assert backlinks["trialstate_links"]


def test_operator_graph_backlinks_include_trialstate_fields_and_overlap():
    backlinks = resolve_operator_graph_backlinks("w")
    trialstate_ids = {item["id"] for item in backlinks["trialstate_links"]}
    assert "weights" in trialstate_ids
    assert "error" in trialstate_ids
    # At least one dependent variable should overlap with operator IO fields.
    assert any(item["trialstate_overlap"] for item in backlinks["graph_backlinks"])


def test_operator_graph_backlink_integrity_cross_registry_consistency():
    validate_operator_graph_backlink_integrity()
    all_backlinks = list_operator_graph_backlinks()
    assert all_backlinks
    assert any(entry["operator"]["id"] == "delta" for entry in all_backlinks)


def test_operator_graph_backlink_unknown_operator_guard():
    with pytest.raises(KeyError):
        resolve_operator_graph_backlinks("not_real_operator")


def test_operator_graph_backlink_integrity_detects_bad_related_operator_type():
    bad_registry = copy.deepcopy(DEPENDENT_VARIABLE_REGISTRY)
    bad_registry["variables"]["prediction_error"]["explainability"]["related_operators"] = "delta"
    with pytest.raises(OperatorGraphBacklinkError, match="must be a list"):
        validate_operator_graph_backlink_integrity_from_payloads(
            dependent=bad_registry,
            operators=copy.deepcopy(OPERATOR_REGISTRY),
            trialstate=copy.deepcopy(TRIALSTATE_FIELD_REGISTRY),
        )
