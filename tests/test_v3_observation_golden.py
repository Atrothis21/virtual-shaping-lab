from __future__ import annotations

import math

import pytest

from virtual_shaping_lab.vsl.agent.observation import build_executable_observation_preset


def test_v3_19_5_identity_observation_golden():
    preset = build_executable_observation_preset("identity_observation")
    out = preset.bundle.step(raw_stimulus={"tone": 1.0, "noise": 0.3})
    assert out.output.feature_names == ["noise", "tone"]
    assert out.output.features == [0.3, 1.0]


def test_v3_19_5_elemental_identity_golden():
    preset = build_executable_observation_preset(
        "elemental_identity",
        stimulus_universe=("tone", "noise", "light"),
    )
    out = preset.bundle.step(raw_stimulus={"tone": 1.0, "light": 0.4})
    assert out.output.feature_names == ["tone", "noise", "light"]
    assert out.output.features == [1.0, 0.0, 0.4]


def test_v3_19_5_configural_identity_golden():
    preset = build_executable_observation_preset(
        "configural_identity",
        stimulus_universe=("tone", "noise", "light"),
    )
    out = preset.bundle.step(raw_stimulus={"tone": 1.0, "noise": 0.6, "light": 0.0})
    assert out.output.feature_names == ["tone", "noise", "light", "cfg:tone&noise"]
    assert out.output.features == [1.0, 0.6, 0.0, 0.6]


def test_v3_19_5_elemental_kernel_generalization_golden():
    preset = build_executable_observation_preset(
        "elemental_kernel_generalization",
        stimulus_universe=("tone", "noise"),
        kernel_sigma=2.0,
    )
    out = preset.bundle.step(raw_stimulus={"tone": 1.0, "noise": 0.5})
    expected_similarity = math.exp(-((1.0**2 + 0.5**2) / (2.0 * 4.0)))
    assert out.output.feature_names == ["tone", "noise", "gen:similarity_kernel"]
    assert out.output.features[0:2] == [1.0, 0.5]
    assert out.output.features[2] == pytest.approx(expected_similarity, abs=1e-12)

