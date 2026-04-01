from __future__ import annotations

import pytest

from virtual_shaping_lab.vsl.protocol import build_executable_protocol_preset


def test_v3_21_5_acquisition_protocol_golden():
    preset = build_executable_protocol_preset("acquisition_protocol", max_trials=3, dt_s=1.0)
    out = preset.bundle.step(action=None)
    assert out.emission.stimulus == {"tone": 1.0}
    assert out.consequence.reward == 1.0
    assert out.advance.t == 1
    assert out.stop.should_stop is False


def test_v3_21_5_differential_protocol_golden():
    preset = build_executable_protocol_preset("differential_protocol", max_trials=3, dt_s=1.0)
    out = preset.bundle.step(action=None)
    assert out.emission.stimulus == {"cs_plus": 1.0}
    assert out.consequence.reward == 1.0
    assert out.metadata["pipeline_order"] == ["emit", "consequence", "advance", "stop", "finalize"]


def test_v3_21_5_operant_protocol_golden():
    preset = build_executable_protocol_preset("operant_protocol", max_trials=3, dt_s=1.0)
    out = preset.bundle.step(action="right")
    assert out.emission.available_actions == ("left", "right")
    assert out.consequence.reward == pytest.approx(0.25, abs=1e-12)
    assert out.advance.dt_s == pytest.approx(1.0, abs=1e-12)


def test_v3_21_5_criterion_shift_protocol_golden():
    preset = build_executable_protocol_preset(
        "criterion_shift_protocol",
        dt_s=1.0,
        criterion_reward_threshold=1.0,
    )
    out = preset.bundle.step(action=None)
    assert out.consequence.reward == 1.0
    assert out.stop.should_stop is True
    assert out.stop.reason == "criterion_reached"
