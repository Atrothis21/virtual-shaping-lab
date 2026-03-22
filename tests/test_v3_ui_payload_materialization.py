from __future__ import annotations

import copy

import pytest

from ui.contracts.preset_materialization import (
    PresetMaterializationError,
    materialize_preset_payload,
    stable_materialized_payload_hash,
    validate_materialized_payload_boundary,
)
from ui.contracts.preset_registry import get_preset


def test_acquisition_materialization_applies_allowed_edits_only():
    payload = materialize_preset_payload(
        "acquisition",
        edits={
            "experiment.program.phases[0].params.n_trials": 20,
            "experiment.program.phases[0].stimuli.cs_plus": ["tone", "noise"],
        },
    )
    phase = payload["experiment"]["program"]["phases"][0]
    assert phase["params"]["n_trials"] == 20
    assert phase["stimuli"]["cs_plus"] == ["tone", "noise"]
    assert payload["report"]["preset"] == "acquisition"


def test_acquisition_materialization_rejects_locked_field_edit():
    with pytest.raises(PresetMaterializationError, match="locked fields"):
        materialize_preset_payload(
            "acquisition",
            edits={"experiment.program.phases[0].protocol": "extinction"},
        )


def test_acquisition_materialization_rejects_undeclared_edit():
    with pytest.raises(PresetMaterializationError, match="undeclared edits"):
        materialize_preset_payload(
            "acquisition",
            edits={"experiment.program.phases[0].params.alpha": 0.9},
        )


def test_acquisition_materialization_is_deterministic():
    edits = {
        "experiment.program.phases[0].params.n_trials": 35,
        "experiment.program.phases[0].stimuli.cs_plus": ["tone"],
        "experiment.agent.learning.rule": "temporal_difference",
    }
    hashes = [stable_materialized_payload_hash(materialize_preset_payload("acquisition", edits=copy.deepcopy(edits))) for _ in range(20)]
    assert len(set(hashes)) == 1


def test_acquisition_materialized_payload_contains_no_undeclared_preset_edits():
    edits = {"experiment.program.phases[0].params.n_trials": 10}
    payload = materialize_preset_payload("acquisition", edits=edits)
    validate_materialized_payload_boundary("acquisition", edits, payload)


def test_acquisition_editable_input_boundary_matches_preset_declared_paths():
    preset = get_preset("acquisition")
    declared = set(preset["ui_contract"]["editability"]["allowed_parameters"])
    assert "experiment.program.phases[0].params.n_trials" in declared
    assert "experiment.program.phases[0].stimuli.cs_plus" in declared
    assert "experiment.agent.learning.rule" in declared

    payload = materialize_preset_payload(
        "acquisition",
        edits={
            "experiment.program.phases[0].params.n_trials": 7,
            "experiment.agent.learning.rule": "rescorla_wagner",
        },
    )
    validate_materialized_payload_boundary(
        "acquisition",
        {
            "experiment.program.phases[0].params.n_trials": 7,
            "experiment.agent.learning.rule": "rescorla_wagner",
        },
        payload,
    )


def test_acquisition_learner_variant_rejects_unsafe_option():
    with pytest.raises(PresetMaterializationError, match="unsupported option"):
        materialize_preset_payload(
            "acquisition",
            edits={"experiment.agent.learning.rule": "unsafe_custom_variant"},
        )


def test_acquisition_learner_variant_allows_safe_options():
    payload_a = materialize_preset_payload(
        "acquisition",
        edits={"experiment.agent.learning.rule": "rescorla_wagner"},
    )
    payload_b = materialize_preset_payload(
        "acquisition",
        edits={"experiment.agent.learning.rule": "temporal_difference"},
    )
    assert payload_a["experiment"]["agent"]["learning"]["rule"] == "rescorla_wagner"
    assert payload_b["experiment"]["agent"]["learning"]["rule"] == "temporal_difference"

