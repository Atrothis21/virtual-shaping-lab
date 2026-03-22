"""Integration surface for V3 UI contract registries."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from ui.contracts.dependent_variable_registry import validate_dependent_variable_registry
from ui.contracts.operator_registry import validate_operator_registry
from ui.contracts.preset_registry import validate_preset_registry
from ui.contracts.trialstate_registry import validate_trialstate_field_registry


class UIRegistryIntegrityError(ValueError):
    """Raised when combined UI registry validation fails."""


def load_ui_registries() -> dict[str, Any]:
    """Load and validate all canonical UI registries."""
    return validate_ui_registry_integrity()


def validate_ui_registry_integrity(
    registries: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Validate trialstate/operator/dependent-variable/preset registries as one surface."""
    source = deepcopy(registries or {})
    raw_trialstate = source.get("trialstate_registry")
    raw_operator = source.get("operator_registry")
    raw_dependent = source.get("dependent_variable_registry")
    raw_preset = source.get("preset_registry")

    try:
        trialstate = validate_trialstate_field_registry(raw_trialstate)
    except Exception as exc:  # pragma: no cover - simple error wrapping
        raise UIRegistryIntegrityError(f"trialstate_registry invalid: {exc}") from exc
    try:
        operator = validate_operator_registry(raw_operator)
    except Exception as exc:  # pragma: no cover - simple error wrapping
        raise UIRegistryIntegrityError(f"operator_registry invalid: {exc}") from exc
    try:
        dependent = validate_dependent_variable_registry(raw_dependent)
    except Exception as exc:  # pragma: no cover - simple error wrapping
        raise UIRegistryIntegrityError(f"dependent_variable_registry invalid: {exc}") from exc
    try:
        preset = validate_preset_registry(raw_preset)
    except Exception as exc:  # pragma: no cover - simple error wrapping
        raise UIRegistryIntegrityError(f"preset_registry invalid: {exc}") from exc

    return {
        "trialstate_registry": trialstate,
        "operator_registry": operator,
        "dependent_variable_registry": dependent,
        "preset_registry": preset,
    }

