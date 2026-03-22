from __future__ import annotations

from ui.contracts.dependent_variable_registry import get_dependent_variable
from ui.contracts.operator_registry import get_operator
from ui.contracts.preset_hardening import (
    build_trial_hover_overlay,
    decode_results_return_state,
    encode_results_return_state,
    validate_preset_form_edits,
)


def test_acquisition_overlay_integrity_registry_driven_only():
    overlay = build_trial_hover_overlay(
        "acquisition",
        variable_id="prediction_error",
        trial_record={
            "prediction": 0.2,
            "outcome": 1.0,
            "error": 0.8,
            "weights": [0.2, 0.4],
            "trial_index": 4,
        },
    )
    assert overlay["registry_driven"] is True
    variable = get_dependent_variable("prediction_error")
    assert overlay["plain_language"] == variable["pedagogy"]["plain_language"]
    assert overlay["related_trialstate_fields"] == variable["explainability"]["related_trialstate_fields"]
    # Ensure no preset-hardcoded operator strings: all operators must resolve from registry.
    expected_ops = set(variable["explainability"]["related_operators"])
    observed_ops = {entry["id"] for entry in overlay["operators"]}
    assert observed_ops == expected_ops
    for entry in overlay["operators"]:
        canonical = get_operator(entry["id"])
        assert entry["operator_view"] == canonical["pedagogy"]["operator_view"]
        assert entry["algebra"] == canonical["pedagogy"]["algebra"]


def test_acquisition_route_state_roundtrip_preserves_config_state():
    encoded = encode_results_return_state(
        preset_id="acquisition",
        edits={
            "experiment.program.phases[0].params.n_trials": 25,
            "experiment.agent.learning.rule": "temporal_difference",
        },
        selected_variable_id="prediction_error",
        scroll_anchor="operators",
    )
    restored = decode_results_return_state(encoded)
    assert restored["preset_id"] == "acquisition"
    assert restored["edits"]["experiment.program.phases[0].params.n_trials"] == 25
    assert restored["edits"]["experiment.agent.learning.rule"] == "temporal_difference"
    assert restored["selected_variable_id"] == "prediction_error"
    assert restored["scroll_anchor"] == "operators"


def test_acquisition_form_validation_polish_returns_structured_errors():
    invalid_locked = validate_preset_form_edits(
        "acquisition",
        {"experiment.program.phases[0].protocol": "extinction"},
    )
    assert invalid_locked["ok"] is False
    assert invalid_locked["error_code"] == "locked_field"
    assert invalid_locked["field_errors"]

    invalid_unknown = validate_preset_form_edits(
        "acquisition",
        {"experiment.program.phases[0].params.alpha": 0.9},
    )
    assert invalid_unknown["ok"] is False
    assert invalid_unknown["error_code"] == "undeclared_edit"
    assert invalid_unknown["field_errors"]

    invalid_option = validate_preset_form_edits(
        "acquisition",
        {"experiment.agent.learning.rule": "unsafe_custom_variant"},
    )
    assert invalid_option["ok"] is False
    assert invalid_option["error_code"] == "unsupported_option"
    assert invalid_option["field_errors"]

