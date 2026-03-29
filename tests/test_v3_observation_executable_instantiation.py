from __future__ import annotations

import pytest

from virtual_shaping_lab.vsl.agent.observation import (
    ExecutableObservationPreset,
    ObservationSpec,
    build_executable_observation_from_spec,
    build_executable_observation_preset,
    executable_observation_preset_names,
)


def test_v3_19_5_executable_observation_preset_names_cover_slice_contract():
    assert executable_observation_preset_names() == [
        "identity_observation",
        "elemental_identity",
        "elemental_context_tag",
        "configural_identity",
        "elemental_kernel_generalization",
    ]


def test_v3_19_5_build_executable_observation_preset_smoke():
    preset = build_executable_observation_preset(
        "elemental_context_tag",
        stimulus_universe=("tone", "noise"),
        context_tags=("A", "B"),
    )
    assert isinstance(preset, ExecutableObservationPreset)
    assert preset.preset_name == "elemental_context_tag"
    out = preset.bundle.step(raw_stimulus={"tone": 1.0}, context_state="B")
    assert out.output.feature_names == ["tone", "noise", "ctx:A", "ctx:B"]
    assert out.output.features == [1.0, 0.0, 0.0, 1.0]


def test_v3_19_5_build_executable_observation_from_spec_supported_mapping():
    spec = ObservationSpec(
        representation="stimulus_vector",
        context="none",
        generalization="stimulus_similarity",
    )
    preset = build_executable_observation_from_spec(
        spec,
        stimulus_universe=("tone", "noise"),
        kernel_sigma=2.0,
    )
    assert preset.preset_name == "elemental_kernel_generalization"
    out = preset.bundle.step(raw_stimulus={"tone": 1.0})
    assert out.output.feature_names[-1] == "gen:similarity_kernel"


def test_v3_19_5_build_executable_observation_from_spec_rejects_unsupported_legal_spec():
    spec = ObservationSpec(
        representation="temporal_basis",
        context="discrete_context",
        generalization="context_gate",
    )
    with pytest.raises(ValueError, match="OBS_E_EXECUTABLE_UNSUPPORTED_SPEC"):
        build_executable_observation_from_spec(spec)

