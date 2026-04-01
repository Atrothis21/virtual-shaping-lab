from __future__ import annotations

import pytest

from virtual_shaping_lab.vsl.protocol import (
    ExecutableProtocolPreset,
    ProtocolSpec,
    build_executable_protocol_from_spec,
    build_executable_protocol_preset,
    executable_protocol_preset_names,
)


def test_v3_21_5_executable_protocol_preset_names_cover_slice_contract():
    assert executable_protocol_preset_names() == [
        "acquisition_protocol",
        "extinction_nonreinforcement_protocol",
        "differential_protocol",
        "compound_protocol",
        "probe_protocol",
        "operant_protocol",
        "concurrent_protocol",
        "criterion_shift_protocol",
    ]


def test_v3_21_5_build_executable_protocol_preset_smoke():
    preset = build_executable_protocol_preset("operant_protocol", max_trials=3)
    assert isinstance(preset, ExecutableProtocolPreset)
    assert preset.preset_name == "operant_protocol"
    out = preset.bundle.step(action="left")
    assert out.emission.available_actions == ("left", "right")
    assert out.consequence.reward == 1.0
    assert out.advance.t == 1


def test_v3_21_5_build_executable_protocol_from_spec_supported_mapping():
    spec = ProtocolSpec(
        emission_rule="classical_trial_emission",
        consequence_rule="deterministic_consequence",
        advance_rule="trial_increment",
        stop_rule="n_trials",
        protocol_family="acquisition",
        action_space_mode="classical_none",
        temporal_mode="trial_discrete",
    )
    preset = build_executable_protocol_from_spec(spec, max_trials=4)
    assert preset.preset_name == "acquisition_protocol"
    out = preset.bundle.step(action=None)
    assert out.consequence.reward == 1.0


def test_v3_21_5_build_executable_protocol_from_spec_rejects_unsupported_legal_spec():
    spec = ProtocolSpec(
        emission_rule="scheduled_emission",
        consequence_rule="deterministic_consequence",
        advance_rule="event_increment",
        stop_rule="session_end",
        protocol_family="custom",
        action_space_mode="binary_response",
        temporal_mode="event_discrete",
    )
    with pytest.raises(ValueError, match="PROTO_E_EXECUTABLE_UNSUPPORTED_SPEC"):
        build_executable_protocol_from_spec(spec)
