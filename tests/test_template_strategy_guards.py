from __future__ import annotations

import pytest

from experiment.phases.public import build_phase
from experiment.phases.templates import (
    AlwaysLearn,
    BlockedSampler,
    FixedSequenceSampler,
    NeverLearn,
    OperantScheduleBuilder,
    PavlovianScheduleBuilder,
    WeightedRandomSampler,
)


class _DummyAgent:
    policy = type("P", (), {"actions": ["left", "right"]})()

    def observe(self, obs):
        return obs

    def act(self, state, actions=None, rng=None):
        return actions[0] if actions else None

    def learn(self, transition):
        return None


@pytest.mark.parametrize(
    "param_key,param_value",
    [
        ("trial_sampler_strategy", "unknown_sampler"),
        ("schedule_builder_strategy", "unknown_builder"),
        ("learning_gate_strategy", "unknown_gate"),
        ("record_builder_strategy", "unknown_record"),
    ],
)
def test_template_phase_rejects_unknown_strategy_keys(param_key, param_value):
    with pytest.raises(ValueError, match=f"Unknown {param_key}"):
        build_phase(
            "acquisition_template",
            agent=_DummyAgent(),
            stimuli={"cs_plus": ["tone"]},
            n_trials=1,
            **{param_key: param_value},
        )


def test_template_phase_accepts_known_trial_sampler_strategies():
    weighted = build_phase(
        "acquisition_template",
        agent=_DummyAgent(),
        stimuli={"cs_plus": ["tone"]},
        n_trials=1,
    )
    assert isinstance(weighted.trial_sampler, WeightedRandomSampler)

    blocked = build_phase(
        "acquisition_template",
        agent=_DummyAgent(),
        stimuli={"cs_plus": ["tone"]},
        n_trials=1,
        trial_sampler_strategy="blocked",
    )
    assert isinstance(blocked.trial_sampler, BlockedSampler)

    fixed = build_phase(
        "acquisition_template",
        agent=_DummyAgent(),
        stimuli={"cs_plus": ["tone"]},
        n_trials=1,
        trial_sampler_strategy="fixed_sequence",
        trial_sampler_sequence=["default"],
    )
    assert isinstance(fixed.trial_sampler, FixedSequenceSampler)


def test_template_phase_accepts_known_schedule_builder_strategies():
    pav = build_phase(
        "acquisition_template",
        agent=_DummyAgent(),
        stimuli={"cs_plus": ["tone"]},
        n_trials=1,
        schedule_builder_strategy="pavlovian",
    )
    assert isinstance(pav.trial_schedule_builder, PavlovianScheduleBuilder)

    op = build_phase(
        "operant_phase_template",
        agent=_DummyAgent(),
        stimuli={"Lever": ["lever"]},
        n_trials=1,
        schedule_builder_strategy="operant",
    )
    assert isinstance(op.trial_schedule_builder, OperantScheduleBuilder)


def test_template_phase_accepts_known_learning_gate_strategies():
    spec_gate = build_phase(
        "acquisition_template",
        agent=_DummyAgent(),
        stimuli={"cs_plus": ["tone"]},
        n_trials=1,
        learning_gate_strategy="spec",
    )
    assert spec_gate.learning_gate.__class__.__name__ == "SpecLearningGate"

    always_gate = build_phase(
        "acquisition_template",
        agent=_DummyAgent(),
        stimuli={"cs_plus": ["tone"]},
        n_trials=1,
        learning_gate_strategy="always",
    )
    assert isinstance(always_gate.learning_gate, AlwaysLearn)

    never_gate = build_phase(
        "acquisition_template",
        agent=_DummyAgent(),
        stimuli={"cs_plus": ["tone"]},
        n_trials=1,
        learning_gate_strategy="never",
    )
    assert isinstance(never_gate.learning_gate, NeverLearn)

