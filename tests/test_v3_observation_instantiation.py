from __future__ import annotations

import itertools

import pytest

from virtual_shaping_lab.vsl.agent.observation import (
    OBSERVATION_INSTANTIATION_FAILURES,
    ObservationInstantiationError,
    ObservationOutput,
    ObservationSpec,
    ObservationSpecValidationError,
    expand_observation_preset,
    instantiate_observation_contracts,
    instantiate_observation_from_boundary,
    materialize_legal_observation_universe,
    observation_preset_names,
    slot_registries,
)


def test_observation_instantiation_materializes_all_legal_presets():
    for preset_name in observation_preset_names():
        spec = expand_observation_preset(preset_name)
        artifact = instantiate_observation_contracts(spec)

        assert artifact.observation_spec.to_dict() == spec.to_dict()
        assert artifact.representation_operator.variant == spec.representation
        assert artifact.context_operator.variant == spec.context
        assert artifact.generalization_operator.variant == spec.generalization
        assert isinstance(artifact.output_template, ObservationOutput)


def test_observation_instantiation_materializes_every_legal_tuple_from_registry_universe():
    regs = slot_registries()
    legal_count = 0
    for representation, context, generalization in itertools.product(
        regs["representation"],
        regs["context"],
        regs["generalization"],
    ):
        try:
            spec = ObservationSpec(
                representation=representation,
                context=context,
                generalization=generalization,
                metadata={"source": "registry_universe"},
            )
        except ObservationSpecValidationError:
            continue
        legal_count += 1
        artifact = instantiate_observation_contracts(spec)
        assert artifact.observation_spec.to_dict() == spec.to_dict()
        assert artifact.representation_operator.variant == spec.representation
        assert artifact.context_operator.variant == spec.context
        assert artifact.generalization_operator.variant == spec.generalization

    assert legal_count > 0


def test_observation_instantiation_rejects_illegal_tuple_before_materialization():
    illegal = {
        "representation": "identity",
        "context": "none",
        "generalization": "context_gate",
        "metadata": {"source": "test"},
    }
    with pytest.raises(ObservationInstantiationError, match="INST_E_LEGALITY"):
        instantiate_observation_contracts(illegal)


def test_observation_instantiation_boundary_resolves_legacy_input_and_materializes():
    artifact = instantiate_observation_from_boundary(
        representation={"name": "temporal_basis"},
        context={"name": "discrete_context"},
        generalization={"name": "context_gate"},
        metadata={"boundary": "test"},
        output_payload={
            "raw_observation": {"cue": "tone"},
            "state_representation": {"x": [1.0, 0.0]},
            "context": {"ctx": "A"},
            "generalized": {"g": [1.0, 0.3]},
            "feature_vector": [1.0, 0.3],
            "feature_labels": ["tone", "sim"],
            "metadata": {"source": "legacy"},
        },
    )
    assert artifact.observation_spec.representation == "temporal_basis"
    assert artifact.observation_spec.context == "discrete_context"
    assert artifact.observation_spec.generalization == "context_gate"
    assert artifact.output_template.feature_names == ["tone", "sim"]


def test_observation_instantiation_failure_catalog_is_machine_readable():
    assert set(OBSERVATION_INSTANTIATION_FAILURES.keys()) == {
        "INST_E_INVALID_SPEC_INPUT",
        "INST_E_LEGALITY",
        "INST_E_BOUNDARY_RESOLUTION",
    }


def test_materialize_legal_observation_universe_returns_non_empty_list():
    artifacts = materialize_legal_observation_universe()
    assert artifacts
    assert all(isinstance(item.observation_spec, ObservationSpec) for item in artifacts)

