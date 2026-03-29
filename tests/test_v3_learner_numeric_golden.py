from __future__ import annotations

import pytest

from virtual_shaping_lab.vsl.agent.learning import build_executable_learner_preset


def test_v3_18_5_rw_acquisition_golden_trajectory():
    executable = build_executable_learner_preset(
        "rescorla_wagner",
        step_size=0.1,
        state={"weights": {"tone": 0.0}},
    )
    bundle = executable.bundle

    predictions: list[float] = []
    for _ in range(5):
        out = bundle.step(features={"tone": 1.0}, reward=1.0, done=False)
        predictions.append(out.prediction)

    assert predictions == pytest.approx(
        [0.0, 0.1, 0.19, 0.271, 0.3439],
        abs=1e-12,
    )
    assert bundle.state["weights"]["tone"] == pytest.approx(0.40951, abs=1e-12)


def test_v3_18_5_rw_extinction_golden_trajectory():
    executable = build_executable_learner_preset(
        "rescorla_wagner",
        step_size=0.1,
        state={"weights": {"tone": 0.0}},
    )
    bundle = executable.bundle

    for _ in range(5):
        bundle.step(features={"tone": 1.0}, reward=1.0, done=False)
    acquired = float(bundle.state["weights"]["tone"])
    assert acquired == pytest.approx(0.40951, abs=1e-12)

    for _ in range(5):
        bundle.step(features={"tone": 1.0}, reward=0.0, done=False)
    extinguished = float(bundle.state["weights"]["tone"])

    assert extinguished == pytest.approx(0.2418115599, abs=1e-12)
    assert extinguished < acquired


def test_v3_18_5_td0_bootstrap_propagation_golden():
    executable = build_executable_learner_preset(
        "td0",
        step_size=0.1,
        gamma=0.9,
        state={"weights": {"s1": 0.0, "s2": 0.0}},
    )
    bundle = executable.bundle

    for _ in range(4):
        bundle.step(
            features={"s1": 1.0, "s2": 0.0},
            next_features={"s1": 0.0, "s2": 1.0},
            reward=0.0,
            done=False,
        )
        bundle.step(
            features={"s1": 0.0, "s2": 1.0},
            reward=1.0,
            done=True,
        )

    assert bundle.state["weights"]["s1"] == pytest.approx(0.04707, abs=1e-12)
    assert bundle.state["weights"]["s2"] == pytest.approx(0.3439, abs=1e-12)
    assert bundle.state["weights"]["s1"] > 0.0

