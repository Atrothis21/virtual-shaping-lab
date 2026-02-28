import numpy as np
import pytest

from experiment.domain.types import ExperimentContext, StepResult
from protocols.base import BaseProtocol
from protocols.blocking import BlockingProtocol
from protocols.conditioned_inhibition import ConditionedInhibitionProtocol
from protocols.extinction import ExtinctionProtocol
from protocols.occasion_setting import OccasionSettingProtocol
from protocols.matching_law import MatchingLawProtocol
from protocols.shaping import ShapingProtocol
from protocols.resurgence import ResurgenceProtocol
from protocols.superextinction import SuperextinctionProtocol
from protocols.spontaneous_recovery import SpontaneousRecoveryProtocol
from protocols.aab_renewal import AABRenewalProtocol
from protocols.aba_renewal import ABARenewalProtocol
from protocols.abc_renewal import ABCRenewalProtocol
from protocols.rapid_reacquisition import RapidReacquisitionProtocol
from protocols.reward_schedules import (
    FixedRatioSchedule,
    VariableRatioSchedule,
    FixedIntervalSchedule,
    VariableIntervalSchedule,
)
from experiment.phases.base import PhaseBase
from domain.types import Observation


class DummyPhase(PhaseBase):
    name = "dummy"

    def __init__(self, agent, n_trials):
        super().__init__(agent=agent, stimuli=["tone"], n_trials=n_trials, params={})

    def sample_trial(self):
        return {"stimulus": "tone"}

    def run_trial(self, trial_spec):
        return {"prediction": 0.0, "reward": 0.0, "state": "s", "action": None}

    def apply_learning(self, trial_spec, outcome):
        return None

    def record_trial(self, trial_spec, outcome):
        return {"phase": self.name, "trial": self.trial_index}

    def reset(self, ctx):
        self.trial_index = 0
        self.records = []
        self._rng = ctx.rng

    def iter_steps(self, ctx):
        if self.trial_index != 0:
            self.reset(ctx)
        while self.has_next_trial():
            record = self.step()
            if record is None:
                continue
            yield StepResult(
                observation=Observation(stimuli=["tone"], context=record.get("context", "A")),
                reward=float(record.get("reward", 0.0)),
                learning_enabled=self.allows_learning,
                done=not self.has_next_trial(),
                metadata={"record": record},
            )


class DummyAgent:
    def reset(self):
        self.was_reset = True


class DummyProtocol(BaseProtocol):
    name = "dummy_protocol"

    def build_phases(self):
        # First phase has 0 trials to hit skip logic.
        self.n_trials = 2
        return [DummyPhase(self.agent, n_trials=0), DummyPhase(self.agent, n_trials=2)]


def test_base_protocol_run_and_reset():
    agent = DummyAgent()
    protocol = DummyProtocol(agent=agent)
    records = protocol.run()
    assert len(records) == 2
    protocol.reset()
    assert protocol.trial_index == 0
    assert protocol.records == []
    assert getattr(agent, "was_reset", False) is True


def test_base_protocol_iter_steps_contract_emits_step_results():
    agent = DummyAgent()
    protocol = DummyProtocol(agent=agent)
    ctx = ExperimentContext(agent=agent, rng=np.random.default_rng(7))
    steps = list(protocol.iter_steps(ctx))
    assert len(steps) == 2
    assert steps[0].metadata.get("record", {}).get("subphase_name") == "dummy"


def test_base_protocol_safety_limit():
    protocol = DummyProtocol(agent=DummyAgent())
    protocol.trial_index = 100
    with pytest.raises(RuntimeError):
        protocol._check_safety_limit(1)


def test_base_protocol_sample_stimulus():
    protocol = DummyProtocol(agent=DummyAgent())
    protocol.stimuli = {"cs_plus": ["tone"]}
    stim, stim_type = protocol.sample_stimulus()
    assert stim_type == "cs_plus"
    assert stim == "tone"

    protocol.stimuli = {"cs_plus": []}
    with pytest.raises(ValueError):
        protocol.sample_stimulus()

    protocol.stimuli = ["tone"]
    with pytest.raises(ValueError):
        protocol.sample_stimulus()


def test_base_protocol_run_safety(monkeypatch):
    proto = DummyProtocol(agent=DummyAgent())
    proto.n_trials = 1

    monkeypatch.setattr(proto, "_max_debug_trials", lambda: -1)
    with pytest.raises(RuntimeError):
        proto.run()

    proto.reset()
    assert proto.trial_index == 0
    assert proto.records == []


def test_base_protocol_sample_stimulus_errors():
    proto = DummyProtocol(agent=DummyAgent(), stimuli=None)
    with pytest.raises(ValueError):
        proto.sample_stimulus()

    proto = DummyProtocol(agent=DummyAgent(), stimuli={"cs_plus": []})
    with pytest.raises(ValueError):
        proto.sample_stimulus()


def test_blocking_protocol_errors():
    proto = BlockingProtocol(agent=DummyAgent(), stimuli={"cs_plus": ["A"]})
    with pytest.raises(ValueError):
        proto.build_phases()


def test_extinction_protocol_errors():
    with pytest.raises(ValueError):
        ExtinctionProtocol(agent=DummyAgent(), stimuli=["tone"])

    proto = ExtinctionProtocol(agent=DummyAgent(), stimuli={"cs_plus": []})
    with pytest.raises(ValueError):
        proto.build_phases()


def test_conditioned_inhibition_errors():
    proto = ConditionedInhibitionProtocol(agent=DummyAgent(), stimuli={})
    with pytest.raises(ValueError):
        proto.build_phases()


def test_occasion_setting_errors():
    proto = OccasionSettingProtocol(agent=DummyAgent(), stimuli={})
    with pytest.raises(ValueError):
        proto.build_phases()


def test_renewal_and_reacquisition_errors():
    for cls in (AABRenewalProtocol, ABARenewalProtocol, ABCRenewalProtocol, RapidReacquisitionProtocol):
        proto = cls(agent=DummyAgent(), stimuli={})
        with pytest.raises(ValueError):
            proto.build_phases()


def test_new_operant_protocols_build_phases():
    proto = ShapingProtocol(
        agent=DummyAgent(),
        stimuli={"cs_plus": ["lever"]},
        params={
            "n_stage_1_trials": 2,
            "n_stage_2_trials": 2,
            "schedule_stage_1": {"type": "fixed_ratio", "value": 1, "reward": 1.0},
            "schedule_stage_2": {"type": "fixed_ratio", "value": 2, "reward": 1.0},
        },
    )
    assert len(proto.build_phases()) == 2

    proto = ResurgenceProtocol(
        agent=DummyAgent(),
        stimuli={"cs_plus": ["lever"]},
        params={
            "n_acquisition_trials": 2,
            "n_suppression_trials": 2,
            "n_resurgence_trials": 2,
            "acquisition_schedule": {"type": "fixed_ratio", "value": 1, "reward": 1.0},
            "suppression_schedule": {"type": "fixed_ratio", "value": 1, "reward": 0.0},
            "resurgence_schedule": {"type": "fixed_ratio", "value": 1, "reward": 1.0},
        },
    )
    assert len(proto.build_phases()) == 3

    proto = SuperextinctionProtocol(
        agent=DummyAgent(),
        stimuli={"cs_plus": ["lever"]},
        params={
            "n_acquisition_trials": 2,
            "n_superextinction_trials": 2,
            "acquisition_schedule": {"type": "fixed_ratio", "value": 1, "reward": 1.0},
            "superextinction_schedule": {"type": "fixed_ratio", "value": 1, "reward": -1.0},
        },
    )
    assert len(proto.build_phases()) == 2

    proto = SpontaneousRecoveryProtocol(
        agent=DummyAgent(),
        stimuli={"cs_plus": ["lever"]},
        params={
            "n_acquisition_trials": 2,
            "n_extinction_trials": 2,
            "n_probe_trials": 2,
            "context_a": "A",
            "context_b": "B",
            "acquisition_schedule": {"type": "fixed_ratio", "value": 1, "reward": 1.0},
            "extinction_schedule": {"type": "fixed_ratio", "value": 1, "reward": 0.0},
            "probe_schedule": {"type": "fixed_ratio", "value": 1, "reward": 0.0},
        },
    )
    assert len(proto.build_phases()) == 5


def test_matching_law_requires_operant():
    class Learner:
        learner_type = "pavlovian"

    class Agent:
        learner = Learner()

    proto = MatchingLawProtocol(agent=Agent())
    with pytest.raises(ValueError):
        proto.validate()


def test_reward_schedules():
    fr = FixedRatioSchedule(n=2, reward=1.0)
    fr.reset()
    assert fr.step(None, 0) == 0.0
    assert fr.step(1, 1) == 0.0
    assert fr.step(1, 2) == 1.0

    vr = VariableRatioSchedule(mean_n=1, reward=1.0)
    vr.reset()
    assert vr.step(None, 0) == 0.0
    _ = vr.step(1, 0)

    fi = FixedIntervalSchedule(interval=2, reward=1.0)
    fi.reset()
    assert fi.step(None, 0) == 0.0
    assert fi.step(1, 1) == 0.0
    assert fi.step(1, 2) == 1.0

    vi = VariableIntervalSchedule(mean_interval=1, reward=1.0)
    vi.reset()
    assert vi.step(None, 0) == 0.0
    _ = vi.step(1, 1)

    fr_punish = FixedRatioSchedule(n=1, reward=-0.5)
    fr_punish.reset()
    assert fr_punish.step(1, 0) == -0.5
