from __future__ import annotations

import pytest

from experiment.domain.types import (
    LearningGateSpec,
    PavlovianContingencySpec,
    PhaseSpec,
    TrialTimeSpec,
    TrialTypeSpec,
)
from experiment.phases.public import build_phase


class _DummyAgent:
    policy = type("P", (), {"actions": ["left", "right"]})()

    def observe(self, obs):
        return obs

    def act(self, state, actions=None, rng=None):
        return actions[0] if actions else None

    def learn(self, transition):
        return None


def test_phase_spec_rejects_unsupported_spec_version():
    with pytest.raises(ValueError, match="Unsupported PhaseSpec.spec_version"):
        PhaseSpec(
            key="template",
            name="Template",
            context_id="A",
            n_trials=1,
            time=TrialTimeSpec(duration_s=1.0, dt_s=0.5),
            trial_types=[TrialTypeSpec(label="A", stimuli=["tone"])],
            contingency=PavlovianContingencySpec(us_magnitude=1.0),
            spec_version=99,
            learning=LearningGateSpec(enabled=True),
        )


@pytest.mark.parametrize(
    "phase_key,stimuli",
    [
        ("acquisition", {"cs_plus": ["tone"]}),
        ("nonreinforcement", {"cs_plus": ["tone"]}),
        ("compound_acquisition", {"compound": ["tone", "noise"]}),
        ("compound_nonreinforcement", {"compound": ["tone", "noise"]}),
        ("differential_acquisition", {"cs_plus": ["tone"], "cs_minus": ["noise"]}),
        ("probe", {"cs_plus": ["tone"]}),
    ],
)
def test_canonical_template_backed_phases_emit_spec_version_1(phase_key, stimuli):
    phase = build_phase(
        phase_key,
        agent=_DummyAgent(),
        stimuli=stimuli,
        n_trials=1,
    )
    assert hasattr(phase, "spec")
    assert phase.spec.spec_version == 1

