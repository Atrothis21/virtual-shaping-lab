from __future__ import annotations

import pytest

from virtual_shaping_lab.vsl.agent.policy import (
    ActionAvailabilityOperator,
    NullPolicyOperator,
    PolicyOperator,
    PolicyOutput,
)


def test_v3_20_5_policy_output_shape_and_copy_semantics():
    output = PolicyOutput(
        action="left",
        action_scores={"left": 1.0},
        action_probabilities={"left": 1.0},
        available_actions=["left", "right"],
        policy_state={"step": 1},
        metadata={"variant": "greedy"},
    )
    assert output.action == "left"
    assert output.available_actions == ("left", "right")
    assert output.action_scores == {"left": 1.0}
    assert output.action_probabilities == {"left": 1.0}
    assert output.policy_state == {"step": 1}
    assert output.metadata["variant"] == "greedy"


def test_v3_20_5_policy_output_rejects_non_object_fields():
    with pytest.raises(ValueError, match="action_scores"):
        PolicyOutput(action=None, action_scores=[])  # type: ignore[arg-type]


def test_v3_20_5_null_policy_operator_emits_no_action_result():
    op = NullPolicyOperator()
    out = op.select(policy_input={}, available_actions=("left", "right"))
    assert out.action is None
    assert out.action_scores == {}
    assert out.action_probabilities == {}
    assert out.available_actions == ("left", "right")
    assert out.metadata["variant"] == "null_policy"


def test_v3_20_5_policy_operator_protocols_are_runtime_checkable():
    class _Policy:
        def select(self, *, policy_input, available_actions=(), rng=None, metadata=None):
            _ = policy_input, available_actions, rng, metadata
            return PolicyOutput(action=None)

    class _Availability:
        def filter_actions(self, *, policy_input, available_actions, metadata=None):
            _ = policy_input, metadata
            return tuple(available_actions)

    assert isinstance(_Policy(), PolicyOperator)
    assert isinstance(_Availability(), ActionAvailabilityOperator)

