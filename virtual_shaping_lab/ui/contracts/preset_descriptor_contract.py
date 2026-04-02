"""Canonical UI preset descriptor contracts for V3 registry-driven pages."""

from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import json
from typing import Any


_NO_POLICY_MARKERS = {"none", "no_policy", "classical_none", "null"}


class UiPresetDescriptorValidationError(ValueError):
    """Raised when a UI preset descriptor violates V3 contract constraints."""


def _stable_json(data: Any) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _require_non_empty_string(value: str, *, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise UiPresetDescriptorValidationError(f"{label} must be a non-empty string.")
    return value.strip()


def _normalize_optional_preset_id(value: str | None, *, label: str) -> str | None:
    if value is None:
        return None
    normalized = _require_non_empty_string(value, label=label)
    if normalized.lower() in _NO_POLICY_MARKERS:
        return "none"
    return normalized


@dataclass(frozen=True)
class UiPresetFieldSpec:
    field_id: str
    label: str
    path: str
    value_type: str
    editable: bool
    required: bool = False
    default: Any = None
    help_text: str | None = None
    options: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "field_id": self.field_id,
            "label": self.label,
            "path": self.path,
            "value_type": self.value_type,
            "editable": self.editable,
            "required": self.required,
            "default": self.default,
            "help_text": self.help_text,
            "options": list(self.options),
        }


@dataclass(frozen=True)
class UiPresetCompatibilityView:
    is_legal: bool
    hidden_fields: tuple[str, ...] = ()
    disabled_fields: tuple[str, ...] = ()
    issues: tuple[str, ...] = ()
    boundary_notes: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "is_legal": self.is_legal,
            "hidden_fields": list(self.hidden_fields),
            "disabled_fields": list(self.disabled_fields),
            "issues": list(self.issues),
            "boundary_notes": list(self.boundary_notes),
        }


@dataclass(frozen=True)
class UiRunPreview:
    policy_trace_enabled: bool
    protocol_trace_enabled: bool
    measurement_output_enabled: bool
    expected_report_sections: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "policy_trace_enabled": self.policy_trace_enabled,
            "protocol_trace_enabled": self.protocol_trace_enabled,
            "measurement_output_enabled": self.measurement_output_enabled,
            "expected_report_sections": list(self.expected_report_sections),
        }


@dataclass(frozen=True)
class UiPresetDescriptor:
    preset_id: str
    title: str
    description: str
    category: str
    family: str
    policy_preset_id: str | None
    protocol_preset_id: str
    measurement_preset_id: str
    editable_fields: tuple[UiPresetFieldSpec, ...] = ()
    locked_parameters: dict[str, Any] = field(default_factory=dict)
    default_parameters: dict[str, Any] = field(default_factory=dict)
    required_action_space_mode: str | None = None
    compatibility: UiPresetCompatibilityView = field(default_factory=lambda: UiPresetCompatibilityView(is_legal=True))
    run_preview: UiRunPreview = field(
        default_factory=lambda: UiRunPreview(
            policy_trace_enabled=False,
            protocol_trace_enabled=True,
            measurement_output_enabled=True,
            expected_report_sections=(),
        )
    )
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "preset_id": self.preset_id,
            "title": self.title,
            "description": self.description,
            "category": self.category,
            "family": self.family,
            "backend_presets": {
                "policy_preset_id": self.policy_preset_id,
                "protocol_preset_id": self.protocol_preset_id,
                "measurement_preset_id": self.measurement_preset_id,
            },
            "editable_fields": [field.to_dict() for field in self.editable_fields],
            "locked_parameters": dict(self.locked_parameters),
            "default_parameters": dict(self.default_parameters),
            "required_action_space_mode": self.required_action_space_mode,
            "compatibility": self.compatibility.to_dict(),
            "run_preview": self.run_preview.to_dict(),
            "metadata": dict(self.metadata),
        }

    def to_json(self) -> str:
        return _stable_json(self.to_dict())

    def stable_hash(self) -> str:
        return hashlib.sha256(self.to_json().encode("utf-8")).hexdigest()


def validate_ui_preset_descriptor(descriptor: UiPresetDescriptor) -> None:
    descriptor_id = _require_non_empty_string(descriptor.preset_id, label="preset_id")
    _require_non_empty_string(descriptor.title, label=f"{descriptor_id}.title")
    _require_non_empty_string(descriptor.description, label=f"{descriptor_id}.description")
    _require_non_empty_string(descriptor.category, label=f"{descriptor_id}.category")
    _require_non_empty_string(descriptor.family, label=f"{descriptor_id}.family")

    _normalize_optional_preset_id(descriptor.policy_preset_id, label=f"{descriptor_id}.policy_preset_id")
    _require_non_empty_string(descriptor.protocol_preset_id, label=f"{descriptor_id}.protocol_preset_id")
    _require_non_empty_string(descriptor.measurement_preset_id, label=f"{descriptor_id}.measurement_preset_id")

    if descriptor.required_action_space_mode is not None:
        _require_non_empty_string(
            descriptor.required_action_space_mode,
            label=f"{descriptor_id}.required_action_space_mode",
        )

    if descriptor.compatibility.issues and descriptor.compatibility.is_legal:
        raise UiPresetDescriptorValidationError(
            f"{descriptor_id}.compatibility cannot declare issues when is_legal is True."
        )

    if descriptor.family == "classical" and descriptor.policy_preset_id not in (None, "none"):
        raise UiPresetDescriptorValidationError(
            f"{descriptor_id}.policy_preset_id must be none for classical family descriptors."
        )

    if descriptor.family in {"operant", "actioned"} and descriptor.policy_preset_id in (None, "none"):
        raise UiPresetDescriptorValidationError(
            f"{descriptor_id}.policy_preset_id is required for operant/actioned descriptors."
        )

    if descriptor.family == "classical" and descriptor.required_action_space_mode not in (None, "classical_none"):
        raise UiPresetDescriptorValidationError(
            f"{descriptor_id}.required_action_space_mode must be 'classical_none' or null for classical family."
        )


@dataclass(frozen=True)
class UiPresetCatalog:
    contract_version: str
    presets: tuple[UiPresetDescriptor, ...]
    categories: tuple[str, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "contract_version": self.contract_version,
            "categories": list(self.categories),
            "presets": [preset.to_dict() for preset in self.presets],
            "metadata": dict(self.metadata),
        }

    def to_json(self) -> str:
        return _stable_json(self.to_dict())

    def stable_hash(self) -> str:
        return hashlib.sha256(self.to_json().encode("utf-8")).hexdigest()


def validate_ui_preset_catalog(catalog: UiPresetCatalog) -> None:
    _require_non_empty_string(catalog.contract_version, label="contract_version")
    seen_ids: set[str] = set()
    for descriptor in catalog.presets:
        validate_ui_preset_descriptor(descriptor)
        if descriptor.preset_id in seen_ids:
            raise UiPresetDescriptorValidationError(f"Duplicate preset_id '{descriptor.preset_id}' in catalog.")
        seen_ids.add(descriptor.preset_id)

