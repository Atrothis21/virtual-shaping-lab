import numpy as np

from experiment.domain.types import EventSpec, ExperimentContext, StepResult, TrialSchedule, TrialTimeSpec, WindowSpec
from experiment.trial_executor import TrialExecutor
from virtual_shaping_lab.experiment.world.schedules import (
    AlwaysAvailable,
    ConstantConsequenceMapper,
    FixedRatioGate,
    TickScheduleRuntime,
)
from virtual_shaping_lab.domain.types import EncodedState, Observation


class DummyAgent:
    def __init__(self):
        self.learn_calls = []
        self.actions = []

    def observe(self, observation):
        return EncodedState(x=[float(len(observation.stimuli))])

    def act(self, state, actions=None, rng=None):
        if actions:
            self.actions.append(actions[0])
            return actions[0]
        return None

    def learn(self, transition):
        self.learn_calls.append(transition)


def test_trial_executor_tick_mode_updates_and_records_per_tick():
    agent = DummyAgent()
    ctx = ExperimentContext(agent=agent, rng=np.random.default_rng(1))
    spec = TrialTimeSpec(
        duration_s=1.0,
        dt_s=0.5,
        events=[
            EventSpec(event_type="stimulus", start_s=0.0, end_s=0.5, metadata={"stimulus": "tone"}),
            EventSpec(event_type="reward", start_s=0.5, end_s=1.0, magnitude=1.0),
        ],
        response_windows=[WindowSpec(start_s=0.0, end_s=1.0, label="all")],
    )
    step = StepResult(observation=Observation(stimuli=[], context="A"), available_actions=["press"], reward=0.0)
    schedule = TrialSchedule(time=spec, base_stimuli=[], available_actions=["press"])

    records = TrialExecutor(update_mode="tick", record_mode="tick").execute(
        ctx=ctx,
        step=step,
        schedule=schedule,
        base_record={"phase": "timed", "trial": 3},
        trial_id=3,
    )

    assert len(records) == 2
    assert records[0]["stimuli"] == ["tone"]
    assert records[1]["reward"] == 1.0
    assert len(agent.learn_calls) == 2
    assert agent.learn_calls[0].trial_step == 0
    assert agent.learn_calls[1].trial_step == 1


def test_trial_executor_trial_record_mode_preserves_trial_record():
    agent = DummyAgent()
    ctx = ExperimentContext(agent=agent, rng=np.random.default_rng(2))
    spec = TrialTimeSpec(duration_s=1.0, dt_s=0.5)
    step = StepResult(observation=Observation(stimuli=[], context="A"), reward=0.0)
    schedule = TrialSchedule(time=spec)
    base = {"phase": "timed", "trial": 1, "prediction": 0.2}

    records = TrialExecutor(update_mode="tick", record_mode="trial").execute(
        ctx=ctx,
        step=step,
        schedule=schedule,
        base_record=base,
        trial_id=1,
    )

    assert records == [base]
    assert len(agent.learn_calls) == 2


def test_trial_executor_uses_schedule_runtime_when_provided():
    agent = DummyAgent()
    ctx = ExperimentContext(agent=agent, rng=np.random.default_rng(3))
    spec = TrialTimeSpec(duration_s=1.0, dt_s=0.5)
    step = StepResult(observation=Observation(stimuli=[], context="A"), available_actions=["press"], reward=0.0)
    schedule_runtime = TickScheduleRuntime(
        availability=AlwaysAvailable(),
        gate=FixedRatioGate(n=2),
        consequence_mapper=ConstantConsequenceMapper(reward=1.0),
    )
    schedule = TrialSchedule(
        time=spec,
        available_actions=["press"],
        metadata={"schedule_runtime": schedule_runtime},
    )

    records = TrialExecutor(update_mode="tick", record_mode="tick").execute(
        ctx=ctx,
        step=step,
        schedule=schedule,
        base_record={"phase": "timed", "trial": 7},
        trial_id=7,
    )

    assert len(records) == 2
    assert records[0]["reward"] == 0.0
    assert records[1]["reward"] == 1.0
    assert records[1]["metadata"]["schedule_runtime_event_type"] == "reinforcement"


def test_trial_executor_debug_flag_defaults_to_false():
    executor = TrialExecutor()
    assert executor.debug is False


def test_trial_executor_accepts_debug_flag_without_behavior_change():
    agent = DummyAgent()
    ctx = ExperimentContext(agent=agent, rng=np.random.default_rng(5))
    spec = TrialTimeSpec(duration_s=1.0, dt_s=0.5)
    step = StepResult(observation=Observation(stimuli=[], context="A"), reward=0.0)
    schedule = TrialSchedule(time=spec)

    records = TrialExecutor(update_mode="trial", record_mode="tick", debug=True).execute(
        ctx=ctx,
        step=step,
        schedule=schedule,
        base_record={"phase": "timed", "trial": 9},
        trial_id=9,
    )

    assert len(records) == 2
    assert all("debug" not in rec for rec in records)
