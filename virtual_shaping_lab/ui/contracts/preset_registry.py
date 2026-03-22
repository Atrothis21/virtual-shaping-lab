"""Thin preset registry contract for V3 UI preset mode."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from ui.contracts.dependent_variable_registry import (
    validate_dependent_variable_ids,
    validate_preset_results_contract,
)
from ui.contracts.operator_registry import list_operator_ids
from ui.contracts.trialstate_registry import list_trialstate_field_ids


class PresetRegistryValidationError(ValueError):
    """Raised when preset registry contract validation fails."""


PRESET_REGISTRY_VERSION = "3.0"

REQUIRED_PRESET_REGISTRY_KEYS: tuple[str, ...] = ("version", "presets")
REQUIRED_PRESET_KEYS: tuple[str, ...] = (
    "id",
    "label",
    "description",
    "protocol_family",
    "registry_bindings",
    "results_contract",
)
REQUIRED_PRESET_BINDING_KEYS: tuple[str, ...] = (
    "trialstate_fields",
    "operators",
    "dependent_variables",
)

PRESET_REGISTRY: dict[str, Any] = {
    "version": PRESET_REGISTRY_VERSION,
    "presets": {
        "acquisition": {
            "id": "acquisition",
            "label": "Acquisition",
            "description": "Canonical acquisition preset contract surface.",
            "protocol_family": "acquisition",
            "registry_bindings": {
                "trialstate_fields": [
                    "stimulus",
                    "prediction",
                    "outcome",
                    "error",
                    "weights",
                    "trial_index",
                    "phase_name",
                ],
                "operators": ["phi", "p", "delta", "w", "m"],
                "dependent_variables": [
                    "associative_strength",
                    "predicted_outcome",
                    "prediction_error",
                    "response_strength",
                ],
            },
            "results_contract": {
                "primary_dependent_variables": [
                    "associative_strength",
                    "predicted_outcome",
                    "prediction_error",
                ],
                "secondary_dependent_variables": ["response_strength"],
                "graph_priority": [
                    "associative_strength",
                    "predicted_outcome",
                    "prediction_error",
                    "response_strength",
                ],
            },
        }
    },
}


def _require_dict(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise PresetRegistryValidationError(f"{label} must be an object.")
    return value


def _require_non_empty_string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise PresetRegistryValidationError(f"{label} must be a non-empty string.")
    return value


def _require_string_list(value: Any, label: str) -> list[str]:
    if not isinstance(value, list):
        raise PresetRegistryValidationError(f"{label} must be a list of strings.")
    out: list[str] = []
    for idx, item in enumerate(value):
        out.append(_require_non_empty_string(item, f"{label}[{idx}]"))
    return out


def validate_preset_registry(registry: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = deepcopy(PRESET_REGISTRY if registry is None else registry)
    root = _require_dict(payload, "preset_registry")

    for key in REQUIRED_PRESET_REGISTRY_KEYS:
        if key not in root:
            raise PresetRegistryValidationError(f"preset_registry missing required key: {key}")

    _require_non_empty_string(root.get("version"), "preset_registry.version")
    presets = _require_dict(root.get("presets"), "preset_registry.presets")

    known_trialstate_fields = set(list_trialstate_field_ids())
    known_operators = set(list_operator_ids())

    seen_ids: set[str] = set()
    for preset_key, raw_preset in presets.items():
        preset = _require_dict(raw_preset, f"preset_registry.presets.{preset_key}")
        for key in REQUIRED_PRESET_KEYS:
            if key not in preset:
                raise PresetRegistryValidationError(
                    f"preset_registry.presets.{preset_key} missing required key: {key}"
                )
        preset_id = _require_non_empty_string(
            preset.get("id"), f"preset_registry.presets.{preset_key}.id"
        )
        if preset_id in seen_ids:
            raise PresetRegistryValidationError(
                f"preset_registry has duplicate preset id: {preset_id}"
            )
        seen_ids.add(preset_id)
        if preset_id != preset_key:
            raise PresetRegistryValidationError(
                f"preset_registry.presets.{preset_key}.id must match preset key '{preset_key}'."
            )
        _require_non_empty_string(
            preset.get("label"), f"preset_registry.presets.{preset_key}.label"
        )
        _require_non_empty_string(
            preset.get("description"), f"preset_registry.presets.{preset_key}.description"
        )
        _require_non_empty_string(
            preset.get("protocol_family"),
            f"preset_registry.presets.{preset_key}.protocol_family",
        )

        bindings = _require_dict(
            preset.get("registry_bindings"),
            f"preset_registry.presets.{preset_key}.registry_bindings",
        )
        for key in REQUIRED_PRESET_BINDING_KEYS:
            if key not in bindings:
                raise PresetRegistryValidationError(
                    f"preset_registry.presets.{preset_key}.registry_bindings missing required key: {key}"
                )

        trial_fields = _require_string_list(
            bindings.get("trialstate_fields"),
            f"preset_registry.presets.{preset_key}.registry_bindings.trialstate_fields",
        )
        operators = _require_string_list(
            bindings.get("operators"),
            f"preset_registry.presets.{preset_key}.registry_bindings.operators",
        )
        dependent_variables = validate_dependent_variable_ids(
            bindings.get("dependent_variables"),
            label=f"preset_registry.presets.{preset_key}.registry_bindings.dependent_variables",
        )

        for field in trial_fields:
            if field not in known_trialstate_fields:
                raise PresetRegistryValidationError(
                    f"preset_registry.presets.{preset_key}.registry_bindings.trialstate_fields "
                    f"references unknown TrialState field: {field}"
                )
        for operator in operators:
            if operator not in known_operators:
                raise PresetRegistryValidationError(
                    f"preset_registry.presets.{preset_key}.registry_bindings.operators "
                    f"references unknown operator id: {operator}"
                )

        try:
            results_contract = validate_preset_results_contract(
                _require_dict(
                    preset.get("results_contract"),
                    f"preset_registry.presets.{preset_key}.results_contract",
                )
            )
        except Exception as exc:
            raise PresetRegistryValidationError(
                f"preset_registry.presets.{preset_key}.results_contract invalid: {exc}"
            ) from exc
        declared_variables = set(dependent_variables)
        for contract_key in (
            "primary_dependent_variables",
            "secondary_dependent_variables",
            "graph_priority",
        ):
            for variable_id in results_contract[contract_key]:
                if variable_id not in declared_variables:
                    raise PresetRegistryValidationError(
                        f"preset_registry.presets.{preset_key}.results_contract.{contract_key} "
                        f"contains undeclared dependent variable: {variable_id}"
                    )

    return payload


def get_preset_registry() -> dict[str, Any]:
    return validate_preset_registry(PRESET_REGISTRY)


def list_preset_ids() -> tuple[str, ...]:
    payload = get_preset_registry()
    return tuple(sorted(payload["presets"].keys()))


def get_preset(preset_id: str) -> dict[str, Any]:
    key = _require_non_empty_string(preset_id, "preset_id")
    payload = get_preset_registry()
    presets = payload["presets"]
    if key not in presets:
        available = ", ".join(sorted(presets.keys()))
        raise KeyError(f"Unknown preset '{key}'. Available presets: {available}")
    return deepcopy(presets[key])
