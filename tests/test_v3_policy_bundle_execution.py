from __future__ import annotations

import numpy as np

from virtual_shaping_lab.vsl.agent.policy import (
    PolicyInput,
    build_executable_policy_preset,
)


def test_v3_20_5_policy_execution_uses_single_stage_operator_dispatch():
    preset = build_executable_policy_preset("epsilon_greedy", epsilon=0.0)
    policy_input = PolicyInput(
        action_values={"left": 0.7, "right": 0.2},
        available_actions=("left", "right"),
    )
    out = preset.policy_operator.select(
        policy_input=policy_input,
        available_actions=policy_input.available_actions,
        rng=np.random.default_rng(5),
    )
    assert out.action == "left"
    assert out.metadata["variant"] == "epsilon_greedy"

