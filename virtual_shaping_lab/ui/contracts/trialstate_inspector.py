"""Expert/pedagogical TrialState inspector contract from field registry."""

from __future__ import annotations

from typing import Any

from ui.contracts.trialstate_registry import get_trialstate_field_registry


class TrialStateInspectorError(ValueError):
    """Raised when TrialState inspector contract resolution fails."""


ALLOWED_INSPECTOR_MODES: tuple[str, ...] = ("preset", "teaching", "expert")


def _require_dict(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise TrialStateInspectorError(f"{label} must be an object.")
    return value


def _require_non_empty_string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise TrialStateInspectorError(f"{label} must be a non-empty string.")
    return value


def _is_visible_in_mode(field: dict[str, Any], *, mode: str) -> bool:
    visibility = _require_dict(field.get("visibility"), f"field.{field.get('id')}.visibility")
    if mode == "preset":
        preset_mode = _require_non_empty_string(
            visibility.get("preset_mode"),
            f"field.{field.get('id')}.visibility.preset_mode",
        )
        return preset_mode.lower() != "hidden"
    if mode == "teaching":
        mechanism_layer = visibility.get("mechanism_layer")
        operator_layer = visibility.get("operator_layer")
        if not isinstance(mechanism_layer, bool) or not isinstance(operator_layer, bool):
            raise TrialStateInspectorError(
                f"field.{field.get('id')}.visibility.mechanism_layer/operator_layer must be boolean."
            )
        return mechanism_layer or operator_layer
    if mode == "expert":
        expert_mode = visibility.get("expert_mode")
        if not isinstance(expert_mode, bool):
            raise TrialStateInspectorError(f"field.{field.get('id')}.visibility.expert_mode must be boolean.")
        return expert_mode
    raise TrialStateInspectorError(f"Unsupported inspector mode '{mode}'.")


def build_trialstate_inspector(
    trial_record: dict[str, Any],
    *,
    mode: str = "expert",
) -> dict[str, Any]:
    if mode not in ALLOWED_INSPECTOR_MODES:
        raise TrialStateInspectorError(
            f"Unsupported inspector mode '{mode}'. Allowed: {', '.join(ALLOWED_INSPECTOR_MODES)}"
        )
    record = _require_dict(trial_record, "trial_record")
    registry = get_trialstate_field_registry()
    groups = _require_dict(registry.get("field_groups"), "trialstate_registry.field_groups")
    fields = _require_dict(registry.get("fields"), "trialstate_registry.fields")

    grouped: dict[str, dict[str, Any]] = {}
    for group_id, raw_group in groups.items():
        group = _require_dict(raw_group, f"trialstate_registry.field_groups.{group_id}")
        grouped[group_id] = {
            "group_id": group_id,
            "label": group.get("label"),
            "description": group.get("description"),
            "fields": [],
        }

    for field_id, raw_field in fields.items():
        field = _require_dict(raw_field, f"trialstate_registry.fields.{field_id}")
        if not _is_visible_in_mode(field, mode=mode):
            continue
        group_id = _require_non_empty_string(field.get("group"), f"trialstate_registry.fields.{field_id}.group")
        if group_id not in grouped:
            raise TrialStateInspectorError(
                f"trialstate_registry.fields.{field_id}.group references unknown group '{group_id}'."
            )
        grouped[group_id]["fields"].append(
            {
                "id": field_id,
                "label": field.get("label"),
                "value": record.get(field_id),
                "present": field_id in record and record.get(field_id) is not None,
            }
        )

    ordered_groups = []
    for group_id in groups.keys():
        block = grouped[group_id]
        if not block["fields"]:
            continue
        block["fields"] = sorted(block["fields"], key=lambda item: str(item["id"]))
        ordered_groups.append(block)

    return {
        "mode": mode,
        "groups": ordered_groups,
    }

