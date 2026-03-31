from __future__ import annotations

import pytest

from virtual_shaping_lab.vsl.agent.policy import (
    POLICY_INSTANTIATION_FAILURES,
    PolicyInstantiationError,
    PolicySpec,
    expand_policy_preset,
    instantiate_policy_contracts,
    instantiate_policy_from_boundary,
    policy_preset_names,
)


def test_policy_instantiation_materializes_all_legal_presets():
    for preset_name in policy_preset_names():
        spec = expand_policy_preset(preset_name)
        artifact = instantiate_policy_contracts(spec)
        assert artifact.policy_spec.to_dict() == spec.to_dict()
        assert artifact.selection_operator.variant == spec.selection_rule
        assert artifact.action_space_mode == spec.action_space_mode


def test_policy_instantiation_rejects_illegal_tuple_before_materialization():
    illegal = {
        "selection_rule": "null",
        "action_space_mode": "discrete",
        "parameters": {},
    }
    with pytest.raises(PolicyInstantiationError, match="INST_E_LEGALITY"):
        instantiate_policy_contracts(illegal)


def test_policy_instantiation_boundary_resolves_runtime_payload():
    artifact = instantiate_policy_from_boundary(
        policy_rule="epsilon_greedy",
        policy_config={
            "selection_rule": "epsilon_greedy",
            "action_space_mode": "discrete",
            "parameters": {"epsilon": 0.15},
            "tie_break_rule": "random",
            "availability_rule": "environment_declared",
        },
        metadata={"source": "boundary"},
    )
    assert isinstance(artifact.policy_spec, PolicySpec)
    assert artifact.policy_spec.selection_rule == "epsilon_greedy"
    assert artifact.policy_spec.parameters["epsilon"] == 0.15


def test_policy_instantiation_failure_catalog_is_machine_readable():
    assert set(POLICY_INSTANTIATION_FAILURES.keys()) == {
        "INST_E_INVALID_SPEC_INPUT",
        "INST_E_LEGALITY",
        "INST_E_BOUNDARY_RESOLUTION",
    }

