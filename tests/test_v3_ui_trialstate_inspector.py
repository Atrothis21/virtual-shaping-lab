from __future__ import annotations

import pytest

from ui.contracts.trialstate_inspector import (
    TrialStateInspectorError,
    build_trialstate_inspector,
)


def _sample_record() -> dict:
    return {
        "stimulus": {"cs_plus": ["tone"]},
        "state": [1.0, 0.0],
        "prediction": 0.4,
        "outcome": 1.0,
        "error": 0.6,
        "weights": [0.1, 0.3],
        "weight_delta": 0.05,
        "associability": 0.8,
        "selected_action": "left",
        "response_strength": 0.7,
        "trial_index": 3,
        "phase_name": "Acquisition",
    }


def test_trialstate_inspector_field_group_rendering_expert_mode():
    panel = build_trialstate_inspector(_sample_record(), mode="expert")
    assert panel["mode"] == "expert"
    assert panel["groups"]
    group_ids = [group["group_id"] for group in panel["groups"]]
    assert "stimulus_input" in group_ids
    assert "prediction" in group_ids
    assert "metadata" in group_ids
    assert all(group["fields"] for group in panel["groups"])


def test_trialstate_inspector_visibility_policy_preset_mode_hidden_fields():
    panel = build_trialstate_inspector(_sample_record(), mode="preset")
    # Current registry marks preset_mode hidden for all fields; preset inspector should be empty.
    assert panel["groups"] == []


def test_trialstate_inspector_visibility_policy_teaching_mode_subset():
    panel = build_trialstate_inspector(_sample_record(), mode="teaching")
    ids = {
        field["id"]
        for group in panel["groups"]
        for field in group["fields"]
    }
    # Teaching mode should include mechanism/operator-layer fields.
    assert "prediction" in ids
    assert "error" in ids
    # Results-only output field should not appear if neither mechanism/operator layer is enabled.
    assert "response_strength" not in ids


def test_trialstate_inspector_rejects_unsupported_mode():
    with pytest.raises(TrialStateInspectorError, match="Unsupported inspector mode"):
        build_trialstate_inspector(_sample_record(), mode="not_a_mode")

