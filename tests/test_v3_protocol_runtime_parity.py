from __future__ import annotations

from virtual_shaping_lab.vsl.protocol import build_executable_protocol_preset
from virtual_shaping_lab.vsl.runtime import build_runtime_protocol_adapter


def test_v3_21_10_runtime_protocol_adapter_matches_bundle_for_normalized_input():
    phase_payload = {
        "t": 0,
        "phase_step": 0,
        "dt_s": 1.0,
        "elapsed_s": 0.0,
        "cumulative_reward": 0.0,
        "context_state": "A",
        "available_actions": ("left", "right"),
        "stimulus": {"lever": 1.0},
    }
    action = "left"

    runtime = build_runtime_protocol_adapter(
        preset_name="operant_protocol",
        max_trials=4,
        dt_s=1.0,
    )
    runtime_out = runtime.step(phase_payload=phase_payload, action=action)

    executable = build_executable_protocol_preset(
        "operant_protocol",
        max_trials=4,
        dt_s=1.0,
    )
    executable.bundle.state.update(
        {
            "t": 0,
            "phase_step": 0,
            "dt_s": 1.0,
            "elapsed_s": 0.0,
            "cumulative_reward": 0.0,
            "context": "A",
            "available_actions": ("left", "right"),
            "stimulus": {"lever": 1.0},
        }
    )
    bundle_out = executable.bundle.step(action=action, metadata={})

    assert runtime_out.emission.stimulus == bundle_out.emission.stimulus
    assert runtime_out.emission.available_actions == bundle_out.emission.available_actions
    assert runtime_out.consequence.reward == bundle_out.consequence.reward
    assert runtime_out.consequence.done == bundle_out.consequence.done
    assert runtime_out.advance.t == bundle_out.advance.t
    assert runtime_out.advance.phase_step == bundle_out.advance.phase_step
    assert runtime_out.advance.dt_s == bundle_out.advance.dt_s
    assert runtime_out.stop.should_stop == bundle_out.stop.should_stop
    assert runtime_out.stop.reason == bundle_out.stop.reason
