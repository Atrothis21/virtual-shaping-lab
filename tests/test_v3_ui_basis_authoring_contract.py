from __future__ import annotations

import copy

import pytest

from ui.contracts.operator_basis_registry import list_ui_selectable_implementations
from ui.contracts.preset_basis_authoring import (
    PresetBasisAuthoringError,
    build_acquisition_basis_authoring_contract,
    materialize_acquisition_basis_payload,
)


def test_acquisition_basis_authoring_contract_is_registry_driven():
    contract = build_acquisition_basis_authoring_contract()
    assert contract["preset_id"] == "acquisition"
    assert contract["registry_generated"] is True
    assert contract["operator_choices"]["phi"] == list(list_ui_selectable_implementations("phi"))
    assert contract["operator_choices"]["w"] == list(list_ui_selectable_implementations("w"))
    assert contract["defaults"]["editable"]["learning_rule_choices"]


def test_acquisition_basis_materialization_emits_canonical_payload_only():
    contract = build_acquisition_basis_authoring_contract()
    payload = materialize_acquisition_basis_payload(
        {
            "preset_id": "acquisition",
            "operator_subset": {
                "phi": contract["defaults"]["operator_subset"]["phi"],
                "w": contract["defaults"]["operator_subset"]["w"],
            },
            "edits": {
                "n_trials": 12,
                "cs_plus": ["tone"],
                "learning_rule": "rescorla_wagner",
            },
        }
    )

    assert set(payload.keys()) == {"experiment", "report", "basis_authoring"}
    assert set(payload["experiment"].keys()) == {"program", "agent", "runtime"}
    phase0 = payload["experiment"]["program"]["phases"][0]
    assert phase0["protocol"] == "acquisition"
    assert phase0["trials"] == 12
    assert phase0["params"]["n_trials"] == 12
    assert payload["report"]["preset"] == "acquisition"


def test_acquisition_basis_materialization_rejects_non_registry_selection():
    contract = build_acquisition_basis_authoring_contract()
    bad = {
        "preset_id": "acquisition",
        "operator_subset": {
            "phi": "not_registry_backed",
            "w": contract["defaults"]["operator_subset"]["w"],
        },
        "edits": {
            "n_trials": 10,
            "cs_plus": ["tone"],
            "learning_rule": "rescorla_wagner",
        },
    }
    with pytest.raises(PresetBasisAuthoringError, match="operator_subset.phi"):
        materialize_acquisition_basis_payload(bad)


def test_acquisition_basis_materialization_learning_rule_to_selection_mapping():
    contract = build_acquisition_basis_authoring_contract()
    payload = materialize_acquisition_basis_payload(
        {
            "preset_id": "acquisition",
            "operator_subset": copy.deepcopy(contract["defaults"]["operator_subset"]),
            "edits": {
                "n_trials": 8,
                "cs_plus": ["tone"],
                "learning_rule": "temporal_difference",
            },
        }
    )
    assert payload["experiment"]["agent"]["learning"]["rule"] == "temporal_difference"
    assert payload["basis_authoring"]["operator_subset"]["w"] == "td0_update"
