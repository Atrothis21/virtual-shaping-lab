from __future__ import annotations

from virtual_shaping_lab.vsl.protocol import ProtocolStepResult
from virtual_shaping_lab.vsl.runtime import RuntimeProtocolAdapter, build_runtime_protocol_adapter


def test_v3_21_10_runtime_protocol_adapter_step_smoke():
    adapter = build_runtime_protocol_adapter(
        preset_name="operant_protocol",
        max_trials=3,
        dt_s=1.0,
    )
    out = adapter.step(
        phase_payload={
            "step_index": 0,
            "stimulus": {"lever": 1.0},
            "context_state": "A",
            "available_actions": ("left", "right"),
            "reward": 1.0,
        },
        action="left",
    )
    assert isinstance(adapter, RuntimeProtocolAdapter)
    assert isinstance(out, ProtocolStepResult)
    assert out.emission.stimulus == {"lever": 1.0}
    assert out.consequence.reward == 1.0
    assert out.advance.t == 1
    assert out.metadata["runtime_protocol"]["normalization"] == "runtime_phase_payload_v1"
    assert out.metadata["pipeline_order"] == ["emit", "consequence", "advance", "stop", "finalize"]


def test_v3_21_10_runtime_protocol_adapter_emit_then_resolve_preserves_causal_split():
    adapter = build_runtime_protocol_adapter(
        preset_name="operant_protocol",
        max_trials=3,
        dt_s=1.0,
    )
    emission = adapter.emit(
        phase_payload={
            "step_index": 0,
            "stimulus": {"lever": 1.0},
            "context_state": "A",
            "available_actions": ("left", "right"),
            "reward": 0.25,
        }
    )
    out = adapter.resolve(action="right")

    assert emission.stimulus == {"lever": 1.0}
    assert emission.available_actions == ("left", "right")
    assert out.consequence.reward == 0.25
    assert out.advance.t == 1


def test_v3_21_10_runtime_protocol_adapter_reset_clears_progress_state():
    adapter = build_runtime_protocol_adapter(
        preset_name="acquisition_protocol",
        max_trials=3,
        dt_s=1.0,
    )
    out1 = adapter.step(
        phase_payload={"step_index": 0, "stimulus": {"tone": 1.0}, "reward": 1.0},
        action=None,
    )
    assert out1.advance.t == 1
    adapter.reset()
    out2 = adapter.step(
        phase_payload={"step_index": 0, "stimulus": {"tone": 1.0}, "reward": 1.0},
        action=None,
    )
    assert out2.advance.t == 1
