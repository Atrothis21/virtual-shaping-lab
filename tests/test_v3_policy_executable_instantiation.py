from __future__ import annotations

import pytest

from virtual_shaping_lab.vsl.agent.policy import (
    EpsilonGreedyPolicy,
    ExecutablePolicyPreset,
    GreedyActionSelectionPolicy,
    NullPolicyOperator,
    PolicySpec,
    build_executable_policy_from_spec,
    build_executable_policy_preset,
    executable_policy_preset_names,
)


def test_v3_20_5_executable_policy_preset_names_cover_slice_contract():
    assert executable_policy_preset_names() == [
        "no_policy",
        "greedy",
        "epsilon_greedy",
        "softmax",
        "uniform_random",
    ]


def test_v3_20_5_build_executable_policy_preset_smoke():
    preset = build_executable_policy_preset("epsilon_greedy", epsilon=0.25)
    assert isinstance(preset, ExecutablePolicyPreset)
    assert preset.preset_name == "epsilon_greedy"
    assert isinstance(preset.policy_operator, EpsilonGreedyPolicy)
    assert preset.policy_spec.parameters["epsilon"] == 0.25


def test_v3_20_5_build_executable_policy_from_spec_supported_mapping():
    spec = PolicySpec(
        selection_rule="greedy",
        action_space_mode="discrete",
        parameters={},
        tie_break_rule="stable_lexicographic",
        availability_rule="environment_declared",
    )
    preset = build_executable_policy_from_spec(spec)
    assert preset.preset_name == "greedy"
    assert isinstance(preset.policy_operator, GreedyActionSelectionPolicy)


def test_v3_20_5_no_policy_maps_to_null_policy_operator():
    spec = PolicySpec(selection_rule="null", action_space_mode="classical_none", parameters={})
    preset = build_executable_policy_from_spec(spec)
    assert preset.preset_name == "no_policy"
    assert isinstance(preset.policy_operator, NullPolicyOperator)


def test_v3_20_5_build_executable_policy_preset_rejects_unknown_name():
    with pytest.raises(ValueError, match="Unknown executable policy preset"):
        build_executable_policy_preset("not_a_preset")

