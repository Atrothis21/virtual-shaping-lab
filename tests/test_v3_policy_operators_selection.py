from __future__ import annotations

import math

import numpy as np
import pytest

from virtual_shaping_lab.vsl.agent.policy import (
    EpsilonGreedyPolicy,
    GreedyActionSelectionPolicy,
    PolicyInput,
    PolicyOutput,
    SoftmaxPolicy,
    UniformRandomPolicy,
)


def _policy_input() -> PolicyInput:
    return PolicyInput(
        action_values={"left": 0.8, "right": 0.2},
        available_actions=("left", "right"),
    )


def test_v3_20_5_greedy_policy_selects_highest_value_action():
    op = GreedyActionSelectionPolicy()
    out = op.select(policy_input=_policy_input(), available_actions=("left", "right"))
    assert isinstance(out, PolicyOutput)
    assert out.action == "left"
    assert out.action_scores == {"left": 0.8, "right": 0.2}
    assert out.metadata["variant"] == "greedy"


def test_v3_20_5_epsilon_greedy_emits_expected_probability_mass():
    op = EpsilonGreedyPolicy(epsilon=0.2, tie_break_rule="random")
    out = op.select(
        policy_input=_policy_input(),
        available_actions=("left", "right"),
        rng=np.random.default_rng(7),
    )
    assert out.action in {"left", "right"}
    assert out.action_probabilities["left"] == pytest.approx(0.9, abs=1e-12)
    assert out.action_probabilities["right"] == pytest.approx(0.1, abs=1e-12)
    assert out.metadata["variant"] == "epsilon_greedy"


def test_v3_20_5_softmax_policy_scores_to_distribution():
    op = SoftmaxPolicy(temperature=1.0)
    out = op.select(
        policy_input={"action_values": {"left": 2.0, "right": 1.0}},
        available_actions=("left", "right"),
        rng=np.random.default_rng(3),
    )
    p_left = math.exp(2.0) / (math.exp(2.0) + math.exp(1.0))
    p_right = math.exp(1.0) / (math.exp(2.0) + math.exp(1.0))
    assert out.action in {"left", "right"}
    assert out.action_probabilities["left"] == pytest.approx(p_left, abs=1e-12)
    assert out.action_probabilities["right"] == pytest.approx(p_right, abs=1e-12)
    assert out.metadata["variant"] == "softmax"


def test_v3_20_5_uniform_random_policy_is_uniform_over_available_actions():
    op = UniformRandomPolicy()
    out = op.select(policy_input={}, available_actions=("left", "right"), rng=np.random.default_rng(11))
    assert out.action in {"left", "right"}
    assert out.action_probabilities == {"left": 0.5, "right": 0.5}
    assert out.action_scores == {"left": 0.0, "right": 0.0}
    assert out.metadata["variant"] == "uniform_random"

