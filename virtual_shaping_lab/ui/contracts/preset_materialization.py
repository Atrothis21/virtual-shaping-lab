"""Preset-mode payload materialization with strict editability boundaries."""

from __future__ import annotations

from copy import deepcopy
import json
import re
from typing import Any

from ui.contracts.preset_registry import get_preset


class PresetMaterializationError(ValueError):
    """Raised when preset payload materialization fails contract checks."""


_PATH_SEGMENT_RE = re.compile(r"^(?P<key>[A-Za-z0-9_]+)(\[(?P<index>\d+)\])?$")


def _parse_path(path: str) -> list[tuple[str, int | None]]:
    parts = [p for p in str(path).split(".") if p]
    if not parts:
        raise PresetMaterializationError("Edit path must be a non-empty dotted path.")
    parsed: list[tuple[str, int | None]] = []
    for part in parts:
        match = _PATH_SEGMENT_RE.match(part)
        if not match:
            raise PresetMaterializationError(f"Unsupported edit path segment syntax: {part}")
        key = match.group("key")
        index_text = match.group("index")
        parsed.append((key, int(index_text) if index_text is not None else None))
    return parsed


def _set_by_path(target: dict[str, Any], path: str, value: Any) -> None:
    parsed = _parse_path(path)
    current: Any = target
    for idx, (key, arr_index) in enumerate(parsed):
        is_last = idx == len(parsed) - 1
        if not isinstance(current, dict):
            raise PresetMaterializationError(f"Edit path '{path}' traversed non-object at '{key}'.")
        if key not in current:
            raise PresetMaterializationError(f"Edit path '{path}' references missing key '{key}'.")
        node = current[key]
        if arr_index is not None:
            if not isinstance(node, list):
                raise PresetMaterializationError(f"Edit path '{path}' expected list at '{key}'.")
            if arr_index < 0 or arr_index >= len(node):
                raise PresetMaterializationError(
                    f"Edit path '{path}' index out of range at '{key}[{arr_index}]'."
                )
            if is_last:
                node[arr_index] = deepcopy(value)
                return
            current = node[arr_index]
            continue
        if is_last:
            current[key] = deepcopy(value)
            return
        current = node


def _collect_leaf_paths(value: Any, *, prefix: str = "") -> set[str]:
    out: set[str] = set()
    if isinstance(value, dict):
        if not value:
            out.add(prefix) if prefix else None
            return out
        for key, sub in value.items():
            next_prefix = f"{prefix}.{key}" if prefix else key
            out |= _collect_leaf_paths(sub, prefix=next_prefix)
        return out
    if isinstance(value, list):
        if not value:
            out.add(prefix) if prefix else None
            return out
        for idx, item in enumerate(value):
            next_prefix = f"{prefix}[{idx}]"
            out |= _collect_leaf_paths(item, prefix=next_prefix)
        return out
    if prefix:
        out.add(prefix)
    return out


def _option_constraints_for_preset(preset: dict[str, Any]) -> dict[str, list[str]]:
    ui_contract = preset.get("ui_contract") if isinstance(preset.get("ui_contract"), dict) else {}
    editability = ui_contract.get("editability") if isinstance(ui_contract.get("editability"), dict) else {}
    constraints = editability.get("option_constraints")
    if not isinstance(constraints, dict):
        return {}
    out: dict[str, list[str]] = {}
    for key, values in constraints.items():
        if isinstance(key, str) and isinstance(values, list):
            out[key] = [str(v) for v in values]
    return out


def materialize_preset_payload(
    preset_id: str,
    edits: dict[str, Any] | None = None,
) -> dict[str, Any]:
    preset = get_preset(preset_id)
    template = preset.get("template")
    if not isinstance(template, dict):
        raise PresetMaterializationError(f"Preset '{preset_id}' is missing template.")

    ui_contract = preset.get("ui_contract")
    if not isinstance(ui_contract, dict):
        raise PresetMaterializationError(f"Preset '{preset_id}' is missing ui_contract.")
    editability = ui_contract.get("editability")
    if not isinstance(editability, dict):
        raise PresetMaterializationError(f"Preset '{preset_id}' is missing ui_contract.editability.")

    allowed_paths = set(str(p) for p in editability.get("allowed_parameters", []) if isinstance(p, str))
    locked_paths = set(str(p) for p in editability.get("locked_parameters", []) if isinstance(p, str))
    constraints = _option_constraints_for_preset(preset)
    requested = edits or {}
    if not isinstance(requested, dict):
        raise PresetMaterializationError("edits must be an object of path -> value.")

    locked_edits = sorted(path for path in requested.keys() if str(path) in locked_paths)
    if locked_edits:
        raise PresetMaterializationError(
            f"Preset '{preset_id}' edits contain locked fields: {', '.join(str(x) for x in locked_edits)}"
        )
    unknown = sorted(path for path in requested.keys() if str(path) not in allowed_paths and str(path) not in locked_paths)
    if unknown:
        raise PresetMaterializationError(
            f"Preset '{preset_id}' contains undeclared edits: {', '.join(str(x) for x in unknown)}"
        )

    for path, allowed_values in constraints.items():
        if path in requested:
            candidate = str(requested[path])
            if candidate not in allowed_values:
                raise PresetMaterializationError(
                    f"Preset '{preset_id}' edit '{path}' has unsupported option '{candidate}'. "
                    f"Allowed: {', '.join(allowed_values)}"
                )

    materialized = deepcopy(template)
    for path in sorted(requested.keys()):
        _set_by_path(materialized, str(path), requested[path])

    payload = {
        "experiment": materialized.get("experiment", {}),
        "report": {"preset": preset_id},
    }
    return payload


def stable_materialized_payload_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def stable_materialized_payload_hash(payload: dict[str, Any]) -> str:
    import hashlib

    return hashlib.sha256(stable_materialized_payload_json(payload).encode("utf-8")).hexdigest()


def validate_materialized_payload_boundary(
    preset_id: str,
    edits: dict[str, Any] | None,
    payload: dict[str, Any],
) -> None:
    expected = materialize_preset_payload(preset_id, edits=edits)
    if stable_materialized_payload_json(expected) != stable_materialized_payload_json(payload):
        raise PresetMaterializationError(
            f"Materialized payload boundary violation for preset '{preset_id}': payload diverges from template+declared-edits."
        )

    preset = get_preset(preset_id)
    template = preset.get("template")
    if not isinstance(template, dict):
        raise PresetMaterializationError(f"Preset '{preset_id}' is missing template.")
    template_experiment = template.get("experiment", {})
    expected_report = {"preset": preset_id}

    if payload.get("report") != expected_report:
        raise PresetMaterializationError(
            f"Materialized payload boundary violation for preset '{preset_id}': report payload must be {expected_report}."
        )

    experiment = payload.get("experiment")
    if not isinstance(experiment, dict):
        raise PresetMaterializationError("Materialized payload must contain experiment object.")

    # Ensure no undeclared top-level experiment keys are introduced relative to template.
    unexpected_keys = sorted(set(experiment.keys()) - set(template_experiment.keys()))
    if unexpected_keys:
        raise PresetMaterializationError(
            f"Materialized payload contains undeclared experiment sections: {', '.join(unexpected_keys)}"
        )

    # Ensure all modifications are explainable by declared edits.
    edits = edits or {}
    ui_contract = preset.get("ui_contract") if isinstance(preset.get("ui_contract"), dict) else {}
    editability = ui_contract.get("editability") if isinstance(ui_contract.get("editability"), dict) else {}
    allowed_paths = set(str(p) for p in editability.get("allowed_parameters", []) if isinstance(p, str))
    if sorted(edits.keys()) != sorted(path for path in edits.keys() if path in allowed_paths):
        raise PresetMaterializationError(
            f"Materialized payload boundary violation for preset '{preset_id}': undeclared edit path detected."
        )

    leaf_paths = _collect_leaf_paths(experiment, prefix="experiment")
    undeclared_leafs = sorted(path for path in leaf_paths if path.startswith("experiment.") and path.endswith(".protocol"))
    if undeclared_leafs and any(path in edits for path in undeclared_leafs):
        raise PresetMaterializationError(
            f"Materialized payload boundary violation for preset '{preset_id}': locked protocol field edited."
        )
