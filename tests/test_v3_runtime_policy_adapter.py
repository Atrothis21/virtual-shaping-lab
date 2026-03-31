from __future__ import annotations

from virtual_shaping_lab.vsl.agent.policy import PolicyOutput
from virtual_shaping_lab.vsl.runtime import RuntimePolicyAdapter, build_runtime_observation_adapter, build_runtime_policy_adapter


def test_v3_20_10_build_runtime_policy_adapter_returns_canonical_runtime_surface():
    adapter = build_runtime_policy_adapter()
    assert isinstance(adapter, RuntimePolicyAdapter)
    assert adapter.preset_name == "no_policy"


def test_v3_20_10_runtime_policy_adapter_selects_action_from_executable_policy_path():
    obs = build_runtime_observation_adapter(preset_name="identity_observation").step(
        stimulus={"cs_plus": ["tone"]},
        context_state="A",
    )
    adapter = build_runtime_policy_adapter(preset_name="greedy")
    out = adapter.step(
        task_input={"stimuli": {"cs_plus": ["tone"]}, "context": "A", "phase": "operant_conditioning", "t": 0},
        observation_output=obs.output,
        prediction={"action_values": {"left": 0.9, "right": 0.1}},
        available_actions=("left", "right"),
    )
    assert isinstance(out, PolicyOutput)
    assert out.action == "left"
    assert out.available_actions == ("left", "right")
    assert out.action_scores == {"left": 0.9, "right": 0.1}
    assert out.metadata["runtime_policy"]["preset_name"] == "greedy"


def test_v3_20_10_runtime_policy_adapter_normalizes_scalar_available_action_payload():
    obs = build_runtime_observation_adapter(preset_name="identity_observation").step(
        stimulus={"cs_plus": ["tone"]},
    )
    adapter = build_runtime_policy_adapter(preset_name="uniform_random")
    out = adapter.step(
        task_input={"stimuli": {"cs_plus": ["tone"]}},
        observation_output=obs.output,
        available_actions="leverpress",
    )
    assert out.available_actions == ("leverpress",)
    assert out.action == "leverpress"

