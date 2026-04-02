"""Registry-driven UI bridge over canonical policy/protocol/measurement presets."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ui.contracts.preset_descriptor_contract import (
    UiPresetCatalog,
    UiPresetCompatibilityView,
    UiPresetDescriptor,
    UiPresetFieldSpec,
    UiRunPreview,
    validate_ui_preset_catalog,
)
from ui.contracts.preset_registry import get_preset, list_preset_ids
from virtual_shaping_lab.vsl.agent.policy.presets import (
    policy_preset_hash,
    policy_preset_names,
    policy_preset_payload,
)
from virtual_shaping_lab.vsl.measurement.presets import (
    measurement_preset_hash,
    measurement_preset_names,
    measurement_preset_payload,
)
from virtual_shaping_lab.vsl.protocol.presets import (
    protocol_preset_hash,
    protocol_preset_names,
    protocol_preset_payload,
)


REGISTRY_BRIDGE_VERSION = "3.23.0"

_PROTOCOL_BY_FAMILY: dict[str, str] = {
    "acquisition": "classical_acquisition",
    "extinction": "classical_extinction",
    "differential_acquisition": "classical_acquisition",
}

_MEASUREMENT_BY_FAMILY: dict[str, str] = {
    "acquisition": "learning_curve_basic",
    "extinction": "extinction_curve",
    "differential_acquisition": "generalization_profile",
}


@dataclass(frozen=True)
class CanonicalPresetReference:
    preset_name: str
    preset_hash: str
    payload: dict[str, Any]


def _discover_presets(
    *,
    names: list[str],
    payload_fn: Any,
    hash_fn: Any,
) -> dict[str, CanonicalPresetReference]:
    out: dict[str, CanonicalPresetReference] = {}
    for name in sorted(names):
        out[name] = CanonicalPresetReference(
            preset_name=name,
            preset_hash=str(hash_fn(name)),
            payload=dict(payload_fn(name)),
        )
    return out


def discover_policy_presets() -> dict[str, CanonicalPresetReference]:
    return _discover_presets(
        names=policy_preset_names(),
        payload_fn=policy_preset_payload,
        hash_fn=policy_preset_hash,
    )


def discover_protocol_presets() -> dict[str, CanonicalPresetReference]:
    return _discover_presets(
        names=protocol_preset_names(),
        payload_fn=protocol_preset_payload,
        hash_fn=protocol_preset_hash,
    )


def discover_measurement_presets() -> dict[str, CanonicalPresetReference]:
    return _discover_presets(
        names=measurement_preset_names(),
        payload_fn=measurement_preset_payload,
        hash_fn=measurement_preset_hash,
    )


def _field_specs_from_preset(preset: dict[str, Any]) -> tuple[UiPresetFieldSpec, ...]:
    ui_contract = preset.get("ui_contract", {})
    editability = ui_contract.get("editability", {}) if isinstance(ui_contract, dict) else {}
    allowed = editability.get("allowed_parameters", []) if isinstance(editability, dict) else []
    specs: list[UiPresetFieldSpec] = []
    for idx, path in enumerate(allowed):
        path_text = str(path).strip()
        if not path_text:
            continue
        label = path_text.split(".")[-1].replace("_", " ").title()
        specs.append(
            UiPresetFieldSpec(
                field_id=f"field_{idx}_{label.lower().replace(' ', '_')}",
                label=label,
                path=path_text,
                value_type="string",
                editable=True,
                required=False,
            )
        )
    return tuple(specs)


def _descriptor_from_ui_preset(
    *,
    preset_id: str,
    policy_refs: dict[str, CanonicalPresetReference],
    protocol_refs: dict[str, CanonicalPresetReference],
    measurement_refs: dict[str, CanonicalPresetReference],
) -> UiPresetDescriptor:
    preset = get_preset(preset_id)
    family = str(preset.get("protocol_family", "")).strip()
    protocol_name = _PROTOCOL_BY_FAMILY.get(family, "classical_acquisition")
    measurement_name = _MEASUREMENT_BY_FAMILY.get(family, "learning_curve_basic")
    if protocol_name not in protocol_refs:
        raise ValueError(f"Unsupported protocol preset mapping for family '{family}'.")
    if measurement_name not in measurement_refs:
        raise ValueError(f"Unsupported measurement preset mapping for family '{family}'.")

    category = "classical"
    policy_name = "classical_none"
    required_action_space_mode = "classical_none"
    if "operant" in family or "action" in family:
        category = "operant"
        policy_name = "operant_greedy"
        required_action_space_mode = "discrete"
    if policy_name not in policy_refs:
        raise ValueError(f"Unsupported policy preset mapping '{policy_name}' for family '{family}'.")

    ui_contract = preset.get("ui_contract", {}) if isinstance(preset.get("ui_contract"), dict) else {}
    editability = ui_contract.get("editability", {}) if isinstance(ui_contract, dict) else {}
    locked = editability.get("locked_parameters", []) if isinstance(editability, dict) else []
    defaults = preset.get("template", {}) if isinstance(preset.get("template"), dict) else {}

    return UiPresetDescriptor(
        preset_id=preset_id,
        title=str(preset.get("label", preset_id)),
        description=str(preset.get("description", "")),
        category=category,
        family=category,
        policy_preset_id="none" if category == "classical" else policy_name,
        protocol_preset_id=protocol_name,
        measurement_preset_id=measurement_name,
        editable_fields=_field_specs_from_preset(preset),
        locked_parameters={str(path): True for path in locked if str(path).strip()},
        default_parameters={"template": defaults},
        required_action_space_mode=required_action_space_mode,
        compatibility=UiPresetCompatibilityView(
            is_legal=True,
            boundary_notes=(
                "protocol owns emit/consequence/advance/stop",
                "agent owns observe/predict/act/learn",
                "measurement is post-run and read-only",
            ),
        ),
        run_preview=UiRunPreview(
            policy_trace_enabled=category != "classical",
            protocol_trace_enabled=True,
            measurement_output_enabled=True,
            expected_report_sections=("protocol_consequence", "measurement_metrics", "measurement_summary"),
        ),
        metadata={
            "ui_bridge_version": REGISTRY_BRIDGE_VERSION,
            "backend_policy_hash": policy_refs[policy_name].preset_hash,
            "backend_protocol_hash": protocol_refs[protocol_name].preset_hash,
            "backend_measurement_hash": measurement_refs[measurement_name].preset_hash,
        },
    )


def build_v3_ui_preset_descriptors() -> tuple[UiPresetDescriptor, ...]:
    policy_refs = discover_policy_presets()
    protocol_refs = discover_protocol_presets()
    measurement_refs = discover_measurement_presets()

    descriptors: list[UiPresetDescriptor] = []
    for preset_id in sorted(list_preset_ids()):
        descriptors.append(
            _descriptor_from_ui_preset(
                preset_id=preset_id,
                policy_refs=policy_refs,
                protocol_refs=protocol_refs,
                measurement_refs=measurement_refs,
            )
        )
    return tuple(descriptors)


def build_v3_ui_preset_catalog() -> UiPresetCatalog:
    catalog = UiPresetCatalog(
        contract_version=REGISTRY_BRIDGE_VERSION,
        categories=("classical", "operant", "measurement", "advanced"),
        presets=build_v3_ui_preset_descriptors(),
        metadata={"registry_driven": True},
    )
    validate_ui_preset_catalog(catalog)
    return catalog

