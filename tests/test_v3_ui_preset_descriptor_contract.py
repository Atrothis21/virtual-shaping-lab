from __future__ import annotations

import pytest

from ui.contracts.preset_descriptor_contract import (
    UiPresetCatalog,
    UiPresetCompatibilityView,
    UiPresetDescriptor,
    UiPresetDescriptorValidationError,
    UiPresetFieldSpec,
    UiRunPreview,
    validate_ui_preset_catalog,
    validate_ui_preset_descriptor,
)


def _classical_descriptor() -> UiPresetDescriptor:
    return UiPresetDescriptor(
        preset_id="acquisition_v3",
        title="Acquisition",
        description="Classical acquisition baseline.",
        category="classical",
        family="classical",
        policy_preset_id="none",
        protocol_preset_id="acquisition_protocol",
        measurement_preset_id="learning_curve_basic",
        editable_fields=(
            UiPresetFieldSpec(
                field_id="n_trials",
                label="Trial Count",
                path="experiment.program.phases[0].params.n_trials",
                value_type="int",
                editable=True,
                required=True,
                default=20,
            ),
        ),
        required_action_space_mode="classical_none",
        compatibility=UiPresetCompatibilityView(is_legal=True),
        run_preview=UiRunPreview(
            policy_trace_enabled=False,
            protocol_trace_enabled=True,
            measurement_output_enabled=True,
            expected_report_sections=("protocol_consequence", "measurement_metrics"),
        ),
    )


def test_v3_ui_preset_descriptor_accepts_classical_none_policy_contract():
    descriptor = _classical_descriptor()
    validate_ui_preset_descriptor(descriptor)
    payload = descriptor.to_dict()
    assert payload["backend_presets"]["policy_preset_id"] == "none"
    assert payload["backend_presets"]["protocol_preset_id"] == "acquisition_protocol"
    assert payload["backend_presets"]["measurement_preset_id"] == "learning_curve_basic"


def test_v3_ui_preset_descriptor_rejects_classical_with_policy_preset():
    descriptor = _classical_descriptor()
    descriptor = UiPresetDescriptor(
        **{
            **descriptor.__dict__,
            "policy_preset_id": "epsilon_greedy",
        }
    )
    with pytest.raises(UiPresetDescriptorValidationError, match="must be none for classical"):
        validate_ui_preset_descriptor(descriptor)


def test_v3_ui_preset_descriptor_rejects_actioned_without_policy():
    descriptor = UiPresetDescriptor(
        preset_id="operant_v3",
        title="Operant",
        description="Actioned operant baseline.",
        category="operant",
        family="operant",
        policy_preset_id="none",
        protocol_preset_id="operant_conditioning",
        measurement_preset_id="action_learning_curve",
        required_action_space_mode="discrete",
    )
    with pytest.raises(UiPresetDescriptorValidationError, match="is required for operant/actioned"):
        validate_ui_preset_descriptor(descriptor)


def test_v3_ui_preset_catalog_hash_is_deterministic_for_same_descriptors():
    descriptor = _classical_descriptor()
    a = UiPresetCatalog(
        contract_version="v3.23.0",
        categories=("classical",),
        presets=(descriptor,),
    )
    b = UiPresetCatalog(
        contract_version="v3.23.0",
        categories=("classical",),
        presets=(descriptor,),
    )
    validate_ui_preset_catalog(a)
    validate_ui_preset_catalog(b)
    assert a.stable_hash() == b.stable_hash()

