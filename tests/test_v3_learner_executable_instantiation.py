from __future__ import annotations

import pytest

from virtual_shaping_lab.vsl.agent.learning import (
    ExecutableLearnerPreset,
    build_executable_learner_from_spec,
    expand_learner_preset,
)


def test_v3_18_5_executable_instantiation_from_symbolic_rw_spec():
    spec = expand_learner_preset("rescorla_wagner")
    executable = build_executable_learner_from_spec(
        spec,
        step_size=0.1,
        state={"weights": {"tone": 0.0}},
    )

    assert isinstance(executable, ExecutableLearnerPreset)
    assert executable.preset_name == "rescorla_wagner"
    out = executable.bundle.step(features={"tone": 1.0}, reward=1.0, done=False)
    assert out.prediction == pytest.approx(0.0, abs=1e-12)
    assert out.error == pytest.approx(1.0, abs=1e-12)


def test_v3_18_5_executable_instantiation_from_symbolic_td0_spec():
    spec = expand_learner_preset("td0")
    executable = build_executable_learner_from_spec(
        spec,
        step_size=0.1,
        gamma=0.9,
        state={"weights": {"s1": 0.0, "s2": 0.0}},
    )

    assert executable.preset_name == "td0"
    out = executable.bundle.step(
        features={"s1": 1.0, "s2": 0.0},
        next_features={"s1": 0.0, "s2": 1.0},
        reward=0.0,
        done=False,
    )
    assert out.error == pytest.approx(0.0, abs=1e-12)


def test_v3_18_5_executable_instantiation_rejects_unsupported_legal_spec():
    spec = expand_learner_preset("q_learning")
    with pytest.raises(ValueError, match="LGR_E_EXECUTABLE_UNSUPPORTED_SPEC"):
        build_executable_learner_from_spec(spec)

