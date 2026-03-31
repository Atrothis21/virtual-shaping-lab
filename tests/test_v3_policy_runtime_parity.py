from __future__ import annotations

from virtual_shaping_lab.vsl.agent.policy import build_executable_policy_preset
from virtual_shaping_lab.vsl.runtime import build_runtime_observation_adapter, build_runtime_policy_adapter


def test_v3_20_10_runtime_policy_adapter_matches_direct_executable_policy_output():
    runtime_adapter = build_runtime_policy_adapter(preset_name="softmax", temperature=1.0)
    executable = build_executable_policy_preset("softmax", temperature=1.0)
    observation_step = build_runtime_observation_adapter(preset_name="identity_observation").step(
        stimulus={"cs_plus": ["tone"], "us": 1.0},
        context_state="A",
    )
    available_actions = ("left", "right")
    prediction = {"action_values": {"left": 2.0, "right": 1.0}}

    runtime_out = runtime_adapter.step(
        task_input={"stimuli": {"cs_plus": ["tone"]}, "context": "A", "phase": "operant_conditioning", "t": 1},
        observation_output=observation_step.output,
        prediction=prediction,
        available_actions=available_actions,
    )

    direct_policy_input = {
        "action_values": {"left": 2.0, "right": 1.0},
        "available_actions": list(available_actions),
    }
    direct_out = executable.policy_operator.select(
        policy_input=direct_policy_input,
        available_actions=available_actions,
        metadata={
            "runtime_policy": {
                "preset_name": "softmax",
                "normalization": "runtime_available_actions_v1",
            }
        },
    )

    assert runtime_out.action == direct_out.action
    assert runtime_out.available_actions == direct_out.available_actions
    assert runtime_out.action_scores == direct_out.action_scores
    assert runtime_out.action_probabilities == direct_out.action_probabilities

