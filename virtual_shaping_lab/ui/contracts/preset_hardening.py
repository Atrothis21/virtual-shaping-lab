"""Acquisition preset hardening contracts for overlays, route-state, and form errors."""

from __future__ import annotations

from copy import deepcopy
import json
from typing import Any

from ui.contracts.dependent_variable_registry import get_dependent_variable
from ui.contracts.operator_registry import get_operator
from ui.contracts.preset_materialization import (
    PresetMaterializationError,
    materialize_preset_payload,
)
from ui.contracts.preset_registry import get_preset


class PresetHardeningError(ValueError):
    """Raised when slice-5 hardening contract checks fail."""


def _require_dict(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise PresetHardeningError(f"{label} must be an object.")
    return value


def _require_non_empty_string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise PresetHardeningError(f"{label} must be a non-empty string.")
    return value


def build_trial_hover_overlay(
    preset_id: str,
    *,
    variable_id: str,
    trial_record: dict[str, Any],
) -> dict[str, Any]:
    preset = get_preset(preset_id)
    _require_dict(preset, "preset")
    record = _require_dict(trial_record, "trial_record")
    variable = get_dependent_variable(variable_id)

    explain = _require_dict(variable.get("explainability"), f"dependent_variable.{variable_id}.explainability")
    related_operators = explain.get("related_operators")
    related_fields = explain.get("related_trialstate_fields")
    hover_fields = explain.get("hover_fields")
    if not isinstance(related_operators, list) or not isinstance(related_fields, list) or not isinstance(hover_fields, list):
        raise PresetHardeningError(
            f"dependent_variable.{variable_id}.explainability must include list fields."
        )

    operator_cards: list[dict[str, Any]] = []
    for op_id in related_operators:
        op = get_operator(str(op_id))
        pedagogy = _require_dict(op.get("pedagogy"), f"operator.{op_id}.pedagogy")
        operator_cards.append(
            {
                "id": op["id"],
                "symbol": op.get("symbol"),
                "name": op.get("name"),
                "stage_index": op.get("stage_index"),
                "operator_view": pedagogy.get("operator_view"),
                "algebra": pedagogy.get("algebra"),
                "reads_trialstate": list(_require_dict(op.get("runtime"), f"operator.{op_id}.runtime").get("reads_trialstate", [])),
                "writes_trialstate": list(_require_dict(op.get("runtime"), f"operator.{op_id}.runtime").get("writes_trialstate", [])),
            }
        )

    observed = {}
    for field in hover_fields:
        key = str(field)
        observed[key] = record.get(key)

    return {
        "preset_id": preset_id,
        "variable_id": variable_id,
        "variable_label": variable.get("label"),
        "plain_language": _require_dict(variable.get("pedagogy"), f"dependent_variable.{variable_id}.pedagogy").get("plain_language"),
        "related_trialstate_fields": [str(f) for f in related_fields],
        "observed_trial_values": observed,
        "operators": sorted(operator_cards, key=lambda card: (int(card.get("stage_index") or 0), str(card.get("id")))),
        "registry_driven": True,
    }


def encode_results_return_state(
    *,
    preset_id: str,
    edits: dict[str, Any],
    selected_variable_id: str | None = None,
    scroll_anchor: str | None = None,
) -> str:
    _require_non_empty_string(preset_id, "preset_id")
    if not isinstance(edits, dict):
        raise PresetHardeningError("edits must be an object.")
    payload = {
        "preset_id": preset_id,
        "edits": deepcopy(edits),
        "selected_variable_id": selected_variable_id,
        "scroll_anchor": scroll_anchor,
    }
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def decode_results_return_state(encoded: str) -> dict[str, Any]:
    raw = _require_non_empty_string(encoded, "encoded")
    try:
        payload = json.loads(raw)
    except Exception as exc:  # pragma: no cover - defensive
        raise PresetHardeningError(f"Invalid return-state payload: {exc}") from exc
    if not isinstance(payload, dict):
        raise PresetHardeningError("Decoded return-state payload must be an object.")
    preset_id = _require_non_empty_string(payload.get("preset_id"), "return_state.preset_id")
    edits = payload.get("edits")
    if not isinstance(edits, dict):
        raise PresetHardeningError("return_state.edits must be an object.")
    return {
        "preset_id": preset_id,
        "edits": deepcopy(edits),
        "selected_variable_id": payload.get("selected_variable_id"),
        "scroll_anchor": payload.get("scroll_anchor"),
    }


def validate_preset_form_edits(
    preset_id: str,
    edits: dict[str, Any],
) -> dict[str, Any]:
    try:
        payload = materialize_preset_payload(preset_id, edits=edits)
    except PresetMaterializationError as exc:
        message = str(exc)
        path = None
        # Best-effort field extraction for form UI highlighting.
        if ": " in message:
            maybe_paths = message.split(": ", 1)[1]
            path = maybe_paths.split(",")[0].strip() if maybe_paths else None
        code = "invalid_edit"
        if "locked fields" in message:
            code = "locked_field"
        elif "undeclared edits" in message:
            code = "undeclared_edit"
        elif "unsupported option" in message:
            code = "unsupported_option"
        return {
            "ok": False,
            "error_code": code,
            "message": message,
            "field_errors": [{"path": path, "message": message}] if path else [],
        }
    return {
        "ok": True,
        "payload": payload,
        "field_errors": [],
    }

