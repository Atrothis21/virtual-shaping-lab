from __future__ import annotations

import pytest

from virtual_shaping_lab.vsl.agent.learning import (
    LEARNER_PRESET_FAMILIES,
    LEARNER_PRESETS,
    PRESET_VERSION,
    ExecutableLearnerPreset,
    LearnerSpec,
    build_executable_learner_preset,
    executable_learner_preset_names,
    expand_learner_preset,
    learner_preset_aliases,
    learner_preset_families,
    learner_preset_hash,
    learner_preset_names,
    learner_preset_payload,
    learner_preset_registry,
)


def test_v3_learner_preset_registry_is_machine_readable():
    names = learner_preset_names()
    registry = learner_preset_registry()
    assert names == sorted(LEARNER_PRESETS.keys())
    assert set(registry.keys()) == set(LEARNER_PRESETS.keys())
    assert all(isinstance(v, list) and len(v) == 6 for v in registry.values())


def test_v3_learner_preset_alias_map_is_machine_readable():
    aliases = learner_preset_aliases()
    assert isinstance(aliases, dict)
    assert "rescorla_wagner" in aliases


def test_v3_learner_preset_expansion_returns_legal_spec_with_traceable_metadata():
    spec = expand_learner_preset("rw")
    assert isinstance(spec, LearnerSpec)
    assert spec.metadata["preset_name"] == "rw"
    assert spec.metadata["preset_version"] == PRESET_VERSION


def test_v3_learner_preset_expansion_supports_aliases():
    direct = expand_learner_preset("rw")
    alias = expand_learner_preset("rescorla_wagner")
    assert alias.trace == direct.trace
    assert alias.predictor == direct.predictor
    assert alias.error == direct.error
    assert alias.attention == direct.attention
    assert alias.updater == direct.updater
    assert alias.policy == direct.policy


def test_v3_learner_preset_unknown_name_fails_fast():
    with pytest.raises(ValueError, match="LGR_E_UNKNOWN_PRESET"):
        expand_learner_preset("not_a_real_preset")


def test_v3_learner_preset_payload_and_hash_are_deterministic():
    payload = learner_preset_payload("q_learning")
    assert payload["preset_name"] == "q_learning"
    assert payload["registry_version"] == PRESET_VERSION

    hashes = [learner_preset_hash("q_learning") for _ in range(20)]
    assert len(set(hashes)) == 1


def test_v3_learner_preset_family_smoke_minimum_three_per_supported_family():
    families = learner_preset_families()
    assert families == LEARNER_PRESET_FAMILIES
    for family, presets in families.items():
        assert len(presets) >= 3, f"{family} must declare at least 3 preset fixtures."
        for preset in presets:
            spec = expand_learner_preset(preset)
            assert isinstance(spec, LearnerSpec)


def test_v3_18_5_executable_learner_presets_cover_rw_and_td0():
    names = executable_learner_preset_names()
    assert "rescorla_wagner" in names
    assert "td0" in names
    assert "pearce_hall_rw" in names
    assert "mackintosh_rw" in names
    assert "td_lambda" in names

    rw = build_executable_learner_preset("rescorla_wagner")
    td0 = build_executable_learner_preset("td0", gamma=0.9)
    ph = build_executable_learner_preset("pearce_hall_rw")
    mk = build_executable_learner_preset("mackintosh_rw")
    tdl = build_executable_learner_preset("td_lambda", gamma=0.9, trace_decay=0.8)

    assert isinstance(rw, ExecutableLearnerPreset)
    assert isinstance(td0, ExecutableLearnerPreset)
    assert isinstance(ph, ExecutableLearnerPreset)
    assert isinstance(mk, ExecutableLearnerPreset)
    assert isinstance(tdl, ExecutableLearnerPreset)
    assert rw.learner_spec.error == "rw_error"
    assert td0.learner_spec.error == "td_error"
    assert ph.learner_spec.attention == "pearce_hall"
    assert mk.learner_spec.attention == "mackintosh"
    assert tdl.learner_spec.trace == "eligibility"

