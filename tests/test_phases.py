import numpy as np
import pytest

from experiment.phases.base import PhaseBase
from experiment.phases.acquisition import AcquisitionPhase
from experiment.phases.nonreinforcement import NonReinforcementPhase
from experiment.phases.differential_acquisition import DifferentialAcquisitionPhase
from experiment.phases.compound_acquisition import CompoundAcquisitionPhase
from experiment.phases.compound_nonreinforcement import CompoundNonReinforcementPhase
from experiment.phases.probe import ProbePhase
from experiment.phases.concurrent_schedule import ConcurrentSchedulePhase
from experiment.phases.context_shift import ContextShiftPhase
from experiment.phases.operant_acquisition import OperantAcquisitionPhase
from experiment.phases.series_helpers import attach_reference_stimuli
from experiment.domain.types import EventSpec, ExperimentContext, TrialTimeSpec


class DummyPhase(PhaseBase):
    name = "dummy"
    allows_learning = True

    def __init__(self, agent=None, n_trials=1, params=None, record=None, stimuli=None):
        super().__init__(agent=agent, stimuli=stimuli or ["tone"], n_trials=n_trials, params=params)
        self._record = record
        self.learn_called = False

    def sample_trial(self):
        return {"stimulus": "tone"}

    def run_trial(self, trial_spec):
        return {"reward": 0.0}

    def apply_learning(self, trial_spec, outcome):
        self.learn_called = True

    def record_trial(self, trial_spec, outcome):
        return self._record if self._record is not None else {"phase": self.name}


def test_validate_requires_prior_learning():
    phase = DummyPhase()
    phase.requires_prior_learning = True
    with pytest.raises(ValueError):
        phase.validate([])


def test_step_short_circuit_when_no_trials():
    phase = DummyPhase(n_trials=0)
    assert phase.step() is None


def test_step_skips_when_record_none():
    phase = DummyPhase(record=None)
    phase._record = None
    phase.record_trial = lambda *_: None
    assert phase.step() is None


def test_step_raises_on_non_dict_record():
    phase = DummyPhase(record="bad")
    with pytest.raises(TypeError):
        phase.step()


def test_context_metadata_inferred():
    phase = DummyPhase()
    phase.context = "B"
    phase.context_source = "inferred"
    record = phase.step()
    assert record["context"] == "B"
    assert record["context_source"] == "inferred"
    assert record["inferred_context"] == "B"


def test_get_phase_summary_default():
    phase = DummyPhase()
    assert phase.get_phase_summary() == {}


class DummyRepresentation:
    attention = None

    def encode(self, observation):
        if hasattr(observation, "stimuli"):
            stimuli = observation.stimuli
        else:
            stimuli = observation.get("stimuli", [])
        return np.asarray([len(stimuli), 1.0], dtype=float)


class DummyLearner:
    alpha = 0.5

    def update(self, transition):
        self.last_update = transition


class DummyAgent:
    def __init__(self, action=None):
        self.representation = DummyRepresentation()
        self.learner = DummyLearner()
        self._action = action
        self.updated = False

    def observe(self, obs):
        return self.representation.encode(obs)

    def value(self, state):
        return float(np.sum(state))

    def act(self, state, actions=None, rng=None):
        return self._action

    def update(self, state, reward, action=None):
        self.updated = True

    def learn(self, transition):
        self.learner.update(transition)
        self.updated = True


def test_phase_base_validation_and_record_errors():
    phase = DummyPhase(agent=DummyAgent(), stimuli=["tone"], n_trials=1)
    phase.requires_prior_learning = True
    with pytest.raises(ValueError):
        phase.validate(history=None)

    phase = DummyPhase(agent=DummyAgent(), stimuli=["tone"], n_trials=1)
    phase.record_trial = lambda *_: None
    assert phase.step() is None

    phase = DummyPhase(agent=DummyAgent(), stimuli=["tone"], n_trials=1)
    phase.record_trial = lambda *_: "bad"
    with pytest.raises(TypeError):
        phase.step()


def test_acquisition_phase_errors():
    with pytest.raises(ValueError):
        AcquisitionPhase(agent=DummyAgent(), stimuli=["tone"], n_trials=1)
    with pytest.raises(ValueError):
        AcquisitionPhase(agent=DummyAgent(), stimuli={"cs_plus": []}, n_trials=1)


def test_compound_phases_errors():
    with pytest.raises(ValueError):
        CompoundAcquisitionPhase(agent=DummyAgent(), stimuli=["tone"], n_trials=1)
    with pytest.raises(ValueError):
        CompoundAcquisitionPhase(agent=DummyAgent(), stimuli={"compound": ["tone"]}, n_trials=1)
    with pytest.raises(ValueError):
        CompoundNonReinforcementPhase(agent=DummyAgent(), stimuli=["tone"], n_trials=1)
    with pytest.raises(ValueError):
        CompoundNonReinforcementPhase(agent=DummyAgent(), stimuli={"compound": ["tone"]}, n_trials=1)


def test_differential_acquisition_errors():
    with pytest.raises(ValueError):
        DifferentialAcquisitionPhase(agent=DummyAgent(), stimuli=["tone"], n_trials=1)
    with pytest.raises(ValueError):
        DifferentialAcquisitionPhase(agent=DummyAgent(), stimuli={"cs_plus": ["a"]}, n_trials=1)
    with pytest.raises(ValueError):
        DifferentialAcquisitionPhase(
            agent=DummyAgent(),
            stimuli={"cs_plus": [], "cs_minus": ["b"]},
            n_trials=1,
        )


def test_nonreinforcement_errors():
    with pytest.raises(ValueError):
        NonReinforcementPhase(agent=DummyAgent(), stimuli=["tone"], n_trials=1)
    with pytest.raises(ValueError):
        NonReinforcementPhase(agent=DummyAgent(), stimuli={"cs_plus": []}, n_trials=1)


def test_probe_errors():
    with pytest.raises(ValueError):
        ProbePhase(agent=DummyAgent(), stimuli=["tone"], n_trials=1)
    with pytest.raises(ValueError):
        ProbePhase(agent=DummyAgent(), stimuli={"cs_plus": []}, n_trials=1)


def test_concurrent_schedule_branches():
    agent = DummyAgent(action="left")
    phase = ConcurrentSchedulePhase(
        agent=agent,
        n_trials=1,
        schedule_left={"type": "fixed_ratio", "value": 1},
        schedule_right={"type": "fixed_ratio", "value": 1},
        params={"action_labels": ["only-one"]},
        stimuli={"cs_plus": ["tone"]},
    )
    record = phase.step()
    assert record["action_label"] in {"left", "right", None}
    assert record["outcome_type"] in {"reinforcement", "extinction", "punishment"}


def test_context_shift_phase_branches():
    phase = ContextShiftPhase(agent=DummyAgent(), context=None, params={"context": "B"})
    outcome = phase.run_trial({})
    record = phase.record_trial({}, outcome)
    assert record["context"] == "B"
    assert phase.apply_learning({}, outcome) is None


def test_operant_acquisition_phase_branches():
    class DummySchedule:
        name = "dummy"
        def reset(self):
            self.reset_called = True
        def step(self, action, t):
            return 1.0

    agent = DummyAgent(action=1)
    phase = OperantAcquisitionPhase(
        agent=agent,
        stimuli={"cs_plus": ["lever"]},
        n_trials=1,
        reward_schedule=DummySchedule(),
    )
    record = phase.step()
    assert record["reward"] == 1.0
    assert record["outcome_type"] == "reinforcement"


def test_operant_and_concurrent_punishment_branch():
    class DummyPunishSchedule:
        name = "punish"

        def reset(self):
            self.reset_called = True

        def step(self, action, t):
            return -1.0 if action is not None else 0.0

    agent = DummyAgent(action=1)
    operant = OperantAcquisitionPhase(
        agent=agent,
        stimuli={"cs_plus": ["lever"]},
        n_trials=1,
        reward_schedule=DummyPunishSchedule(),
    )
    operant_record = operant.step()
    assert operant_record["reward"] == -1.0
    assert operant_record["outcome_type"] == "punishment"

    concurrent = ConcurrentSchedulePhase(
        agent=DummyAgent(action="left"),
        n_trials=1,
        schedule_left={"type": "fixed_ratio", "value": 1, "reward": -1.0},
        schedule_right={"type": "fixed_ratio", "value": 1, "reward": 1.0},
        params={"action_labels": ["left", "right"]},
        stimuli={"cs_plus": ["tone"]},
    )
    concurrent_record = concurrent.step()
    assert concurrent_record["reward"] == -1.0
    assert concurrent_record["outcome_type"] == "punishment"
    assert concurrent_record["reward_action"] == 0


def test_nonreinforcement_reference_series():
    agent = DummyAgent(action=None)
    phase = NonReinforcementPhase(
        agent=agent,
        stimuli={"cs_plus": ["tone", "noise"]},
        n_trials=1,
        params={},
    )
    record = phase.step()
    assert "series_values" in record


def test_probe_phase_reward_branch():
    agent = DummyAgent(action=None)
    phase = ProbePhase(
        agent=agent,
        stimuli={"cs_plus": ["tone"]},
        n_trials=1,
        params={"deliver_reward": True, "reward_value": 0.5},
    )
    record = phase.step()
    assert record["reward"] == 0.5


def test_attach_reference_stimuli_sets_reference():
    class DummyPhaseObj:
        def __init__(self, stimuli):
            self.stimuli = stimuli
            self.params = {}

    phases = [DummyPhaseObj(["tone", "noise"]), DummyPhaseObj(["tone"])]
    attach_reference_stimuli(phases)
    assert phases[1].params["reference_stimuli"] == ["noise"]


def test_acquisition_phase_smoke(dummy_agent):
    phase = AcquisitionPhase(
        agent=dummy_agent,
        stimuli={"cs_plus": ["tone"]},
        n_trials=2,
        params={"outcome": 1.0},
    )
    record = phase.step()
    assert record["phase"] == "acquisition"
    assert "context" in record


def test_nonreinforcement_phase_smoke(dummy_agent):
    phase = NonReinforcementPhase(
        agent=dummy_agent,
        stimuli={"cs_plus": ["tone"]},
        n_trials=1,
        params={"alpha": 0.2, "gamma": 0},
    )
    record = phase.step()
    assert record["phase"] == "nonreinforcement"


def test_differential_phase_smoke(dummy_agent):
    phase = DifferentialAcquisitionPhase(
        agent=dummy_agent,
        stimuli={"cs_plus": ["tone"], "cs_minus": ["noise"]},
        n_trials=2,
        reinforced_outcome=1.0,
        params={"alpha": 0.2, "gamma": 0},
    )
    record = phase.step()
    assert record["phase"] == "differential_acquisition"


def test_compound_acquisition_phase_smoke(dummy_agent):
    phase = CompoundAcquisitionPhase(
        agent=dummy_agent,
        stimuli={"compound": ["tone", "noise"]},
        n_trials=1,
        params={"alpha_cs1": 0.2, "alpha_cs2": 0.12, "gamma": 0},
    )
    record = phase.step()
    assert record["phase"] == "compound_acquisition"


def test_compound_nonreinforcement_phase_smoke(dummy_agent):
    phase = CompoundNonReinforcementPhase(
        agent=dummy_agent,
        stimuli={"compound": ["tone", "noise"]},
        n_trials=1,
        params={"alpha": 0.2, "gamma": 0},
    )
    record = phase.step()
    assert record["phase"] == "compound_nonreinforcement"


def test_acquisition_phase_supports_iter_steps_contract(dummy_agent):
    phase = AcquisitionPhase(
        agent=dummy_agent,
        stimuli={"cs_plus": ["tone"]},
        n_trials=2,
        params={"outcome": 1.0},
    )
    ctx = ExperimentContext(agent=dummy_agent, rng=np.random.default_rng(7))
    steps = list(phase.iter_steps(ctx))
    assert len(steps) == 2
    assert steps[-1].done is True
    assert steps[0].metadata.get("record", {}).get("phase") == "acquisition"


def test_operant_acquisition_phase_supports_iter_steps_contract():
    class DummySchedule:
        name = "dummy"
        def reset(self):
            self.reset_called = True
        def step(self, action, t):
            return 1.0

    agent = DummyAgent(action=1)
    phase = OperantAcquisitionPhase(
        agent=agent,
        stimuli={"cs_plus": ["lever"]},
        n_trials=2,
        reward_schedule=DummySchedule(),
    )
    ctx = ExperimentContext(agent=agent, rng=np.random.default_rng(9))
    steps = list(phase.iter_steps(ctx))
    assert len(steps) == 2
    assert steps[-1].done is True
    assert steps[0].metadata.get("record", {}).get("phase") == "operant_acquisition"


def test_nonreinforcement_phase_supports_iter_steps_contract(dummy_agent):
    phase = NonReinforcementPhase(
        agent=dummy_agent,
        stimuli={"cs_plus": ["tone"]},
        n_trials=2,
        params={},
    )
    ctx = ExperimentContext(agent=dummy_agent, rng=np.random.default_rng(11))
    steps = list(phase.iter_steps(ctx))
    assert len(steps) == 2
    assert steps[-1].done is True
    assert steps[0].metadata.get("record", {}).get("phase") == "nonreinforcement"


def test_differential_phase_supports_iter_steps_contract(dummy_agent):
    phase = DifferentialAcquisitionPhase(
        agent=dummy_agent,
        stimuli={"cs_plus": ["tone"], "cs_minus": ["noise"]},
        n_trials=2,
        params={},
    )
    ctx = ExperimentContext(agent=dummy_agent, rng=np.random.default_rng(13))
    steps = list(phase.iter_steps(ctx))
    assert len(steps) == 2
    assert steps[-1].done is True
    assert steps[0].metadata.get("record", {}).get("phase") == "differential_acquisition"


def test_nonreinforcement_build_trial_schedule_attaches_metadata(dummy_agent):
    spec = TrialTimeSpec(
        duration_s=1.0,
        dt_s=0.5,
        events=[EventSpec(event_type="stimulus", start_s=0.0, end_s=1.0)],
    )
    phase = NonReinforcementPhase(
        agent=dummy_agent,
        stimuli={"cs_plus": ["tone"]},
        n_trials=1,
        params={"trial_time_spec": spec},
    )
    ctx = ExperimentContext(agent=dummy_agent, rng=np.random.default_rng(17))
    step = list(phase.iter_steps(ctx))[0]
    assert step.metadata.get("trial_schedule") is not None

