from __future__ import annotations

import math

import pytest

from virtual_shaping_lab.vsl.agent.policy import PolicyInput, build_executable_policy_preset


def test_v3_20_5_greedy_policy_golden():
    preset = build_executable_policy_preset("greedy")
    out = preset.policy_operator.select(
        policy_input=PolicyInput(action_values={"left": 1.0, "right": 0.5}),
        available_actions=("left", "right"),
    )
    assert out.action == "left"
    assert out.action_scores == {"left": 1.0, "right": 0.5}


def test_v3_20_5_softmax_policy_golden_probabilities():
    preset = build_executable_policy_preset("softmax", temperature=1.0)
    out = preset.policy_operator.select(
        policy_input=PolicyInput(action_values={"left": 2.0, "right": 1.0}),
        available_actions=("left", "right"),
    )
    expected_left = math.exp(2.0) / (math.exp(2.0) + math.exp(1.0))
    expected_right = math.exp(1.0) / (math.exp(2.0) + math.exp(1.0))
    assert out.action_probabilities["left"] == pytest.approx(expected_left, abs=1e-12)
    assert out.action_probabilities["right"] == pytest.approx(expected_right, abs=1e-12)


def test_v3_20_5_uniform_random_policy_golden_probabilities():
    preset = build_executable_policy_preset("uniform_random")
    out = preset.policy_operator.select(
        policy_input=PolicyInput(),
        available_actions=("left", "right", "noop"),
    )
    assert out.action in {"left", "right", "noop"}
    assert out.action_probabilities == {
        "left": pytest.approx(1.0 / 3.0, abs=1e-12),
        "right": pytest.approx(1.0 / 3.0, abs=1e-12),
        "noop": pytest.approx(1.0 / 3.0, abs=1e-12),
    }


def test_v3_20_5_no_policy_golden_no_action():
    preset = build_executable_policy_preset("no_policy")
    out = preset.policy_operator.select(policy_input=PolicyInput())
    assert out.action is None
    assert out.available_actions == ()

