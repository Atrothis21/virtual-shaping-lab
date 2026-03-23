from __future__ import annotations

import pytest

from ui.contracts.trial_hover_explainability import (
    TrialHoverExplainabilityError,
    build_trial_hover_explainability_panel,
)


def test_trial_hover_overlay_field_resolution_from_registry_hooks():
    panel = build_trial_hover_explainability_panel(
        "prediction_error",
        trial_record={
            "prediction": 0.1,
            "outcome": 1.0,
            "error": 0.9,
            "weight_delta": 0.05,
            "weights": [0.1, 0.2],
        },
    )
    assert panel["variable_id"] == "prediction_error"
    assert panel["variable_label"]
    assert panel["plain_language"]
    assert panel["field_resolution"]
    assert panel["operator_links"]

    resolved_ids = {item["field_id"] for item in panel["field_resolution"]}
    assert {"prediction", "outcome", "error"}.issubset(resolved_ids)


def test_trial_hover_overlay_surfaces_prediction_outcome_error_update_links_when_available():
    panel = build_trial_hover_explainability_panel(
        "prediction_error",
        trial_record={
            "prediction": 0.4,
            "outcome": 0.0,
            "error": -0.4,
            "weight_delta": -0.1,
        },
    )
    links = {item["field_id"] for item in panel["core_links"]}
    assert {"prediction", "outcome", "error", "weight_delta"}.issubset(links)


def test_trial_hover_overlay_missing_fields_degrades_gracefully():
    panel = build_trial_hover_explainability_panel(
        "prediction_error",
        trial_record={},
    )
    assert panel["graceful_degradation"] is True
    assert panel["field_resolution"]
    assert all(item["present"] is False for item in panel["field_resolution"])
    assert panel["core_links"] == []


def test_trial_hover_overlay_rejects_non_object_trial_record():
    with pytest.raises(TrialHoverExplainabilityError, match="trial_record must be an object"):
        build_trial_hover_explainability_panel("prediction_error", trial_record=None)  # type: ignore[arg-type]

