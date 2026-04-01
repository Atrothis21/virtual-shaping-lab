from __future__ import annotations

import pytest

from virtual_shaping_lab.vsl.protocol import (
    PROTO_INSTANTIATION_FAILURES,
    ProtocolInstantiationError,
    ProtocolSpec,
    expand_protocol_preset,
    instantiate_protocol_contracts,
    instantiate_protocol_from_boundary,
    protocol_preset_names,
)


def test_protocol_instantiation_materializes_all_legal_presets():
    for preset_name in protocol_preset_names():
        spec = expand_protocol_preset(preset_name)
        artifact = instantiate_protocol_contracts(spec)
        assert artifact.protocol_spec.to_dict() == spec.to_dict()
        assert artifact.emission_operator.variant == spec.emission_rule
        assert artifact.consequence_operator.variant == spec.consequence_rule
        assert artifact.protocol_family == spec.protocol_family


def test_protocol_instantiation_rejects_illegal_tuple_before_materialization():
    illegal = {
        "emission_rule": "operant_offer_emission",
        "consequence_rule": "deterministic_consequence",
        "advance_rule": "trial_increment",
        "stop_rule": "n_trials",
        "protocol_family": "operant_conditioning",
        "action_space_mode": "classical_none",
        "temporal_mode": "trial_discrete",
    }
    with pytest.raises(ProtocolInstantiationError, match="INST_E_LEGALITY"):
        instantiate_protocol_contracts(illegal)


def test_protocol_instantiation_boundary_resolves_runtime_payload():
    artifact = instantiate_protocol_from_boundary(
        protocol_rule="operant_conditioning",
        protocol_config={
            "protocol_family": "operant_conditioning",
            "emission_rule": "operant_offer_emission",
            "consequence_rule": "scheduled_consequence",
            "advance_rule": "trial_increment",
            "stop_rule": "n_trials",
            "action_space_mode": "discrete",
            "temporal_mode": "trial_discrete",
        },
        metadata={"source": "boundary"},
    )
    assert isinstance(artifact.protocol_spec, ProtocolSpec)
    assert artifact.protocol_spec.protocol_family == "operant_conditioning"
    assert artifact.protocol_spec.action_space_mode == "discrete"


def test_protocol_instantiation_failure_catalog_is_machine_readable():
    assert set(PROTO_INSTANTIATION_FAILURES.keys()) == {
        "INST_E_INVALID_SPEC_INPUT",
        "INST_E_LEGALITY",
        "INST_E_BOUNDARY_RESOLUTION",
    }
