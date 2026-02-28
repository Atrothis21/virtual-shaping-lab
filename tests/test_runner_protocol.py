from typing import Any, Dict, List

from experiment.runner import Runner
from experiment.sinks import InMemorySink
from experiment.phases.base import PhaseBase
from experiment.domain.types import EventSpec, StepResult, TrialSchedule, TrialTimeSpec
from protocols.base import BaseProtocol
from domain.types import Observation


class DummyPhase(PhaseBase):
    name = "dummy"

    def __init__(self, agent, n_trials=2):
        super().__init__(agent=agent, stimuli=["tone"], n_trials=n_trials, params={})

    def sample_trial(self) -> Dict[str, Any]:
        return {"stimulus": "tone"}

    def run_trial(self, trial_spec: Dict[str, Any]) -> Any:
        return {"reward": 0.0, "state": trial_spec["stimulus"], "prediction": 0.5, "action": None}

    def apply_learning(self, trial_spec: Dict[str, Any], outcome: Any) -> None:
        return None

    def record_trial(self, trial_spec: Dict[str, Any], outcome: Any) -> Dict[str, Any]:
        return {
            "phase": self.name,
            "trial": self.trial_index,
            "prediction": outcome["prediction"],
        }

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


class LegacyOnlyPhase(PhaseBase):
    name = "legacy_only"

    def __init__(self, agent, n_trials=1):
        super().__init__(agent=agent, stimuli=["tone"], n_trials=n_trials, params={})

    def sample_trial(self):
        return {"stimulus": "tone"}

    def run_trial(self, trial_spec):
        return {"reward": 0.0, "state": "s", "prediction": 0.5, "action": None}

    def apply_learning(self, trial_spec, outcome):
        return None

    def record_trial(self, trial_spec, outcome):
        return {"phase": self.name, "trial": self.trial_index, "prediction": outcome["prediction"]}


class DummyProtocol(BaseProtocol):
    name = "dummy_protocol"

    def build_phases(self) -> List[Any]:
        self.n_trials = 2
        return [DummyPhase(self.agent, n_trials=2)]


class DummyAgent:
    def reset(self):
        return None

    def observe(self, observation):
        return observation

    def update(self, state, reward, action=None):
        return None

    def value(self, state, action=None):
        return 0.5


class DummyRunnableUnit:
    def __init__(self):
        self.reset_called = False

    def reset(self, ctx):
        self.reset_called = True

    def iter_steps(self, ctx):
        yield StepResult(
            observation=Observation(stimuli=["tone"], context="A"),
            reward=0.1,
            done=False,
            metadata={"record": {"phase": "iter_phase", "trial": 0, "prediction": 0.2}},
        )
        yield StepResult(
            observation=Observation(stimuli=["tone"], context="A"),
            reward=0.2,
            done=True,
            metadata={"record": {"phase": "iter_phase", "trial": 1, "prediction": 0.3}},
        )


class SeededRunnableUnit:
    def reset(self, ctx):
        return None

    def iter_steps(self, ctx):
        # Deterministic given runner seed/context RNG.
        reward = float(ctx.rng.integers(0, 1000))
        yield StepResult(
            observation=Observation(stimuli=["tone"], context="A"),
            reward=reward,
            done=True,
            metadata={"record": {"phase": "seeded", "trial": 0, "reward": reward}},
        )


class TimedRunnableUnit:
    def reset(self, ctx):
        return None

    def iter_steps(self, ctx):
        spec = TrialTimeSpec(
            duration_s=1.0,
            dt_s=0.5,
            events=[
                EventSpec(event_type="stimulus", start_s=0.0, end_s=0.5, metadata={"stimulus": "tone"}),
                EventSpec(event_type="reward", start_s=0.5, end_s=1.0, magnitude=1.0),
            ],
        )
        yield StepResult(
            observation=Observation(stimuli=[], context="A"),
            reward=0.0,
            done=True,
            metadata={
                "record": {"phase": "timed", "trial": 0},
                "trial_schedule": TrialSchedule(time=spec, available_actions=[]),
            },
        )


def test_runner_handles_phase():
    agent = DummyAgent()
    phase = DummyPhase(agent, n_trials=1)
    runner = Runner(phase)
    records = runner.run()
    assert len(records) == 1
    assert records[0]["phase_name"] == "dummy"


def test_runner_handles_protocol():
    agent = DummyAgent()
    protocol = DummyProtocol(agent=agent)
    runner = Runner(protocol)
    records = runner.run()
    assert len(records) == 2
    assert records[0]["subphase_name"] == "dummy"


def test_runner_handles_runnable_unit_iter_steps():
    unit = DummyRunnableUnit()
    runner = Runner(unit)
    records = runner.run()
    assert unit.reset_called is True
    assert len(records) == 2
    assert records[0]["phase_name"] == "iter_phase"


def test_runner_seed_controls_runnable_unit_rng_deterministically():
    r1 = Runner(SeededRunnableUnit(), seed=123).run()
    r2 = Runner(SeededRunnableUnit(), seed=123).run()
    r3 = Runner(SeededRunnableUnit(), seed=456).run()

    assert r1[0]["reward"] == r2[0]["reward"]
    assert r1[0]["reward"] != r3[0]["reward"]


def test_runner_emits_to_sink_and_returns_records():
    agent = DummyAgent()
    phase = DummyPhase(agent, n_trials=1)
    sink = InMemorySink()
    runner = Runner(phase, sink=sink)
    records = runner.run()
    assert len(records) == 1
    assert sink.records == records
    assert sink.closed is False


def test_runner_record_mode_tick_emits_tick_records_for_timed_schedule():
    records = Runner(
        TimedRunnableUnit(),
        settings={"record_mode": "tick"},
    ).run()
    assert len(records) == 2
    assert records[0]["phase_name"] == "timed"
    assert records[0]["tick"] == 0
    assert records[1]["reward"] == 1.0


def test_runner_strict_mode_blocks_legacy_phase_fallback():
    agent = DummyAgent()
    phase = LegacyOnlyPhase(agent, n_trials=1)
    runner = Runner(phase, settings={"strict_mode": True})
    try:
        runner.run()
        assert False, "Expected strict mode to reject legacy phase fallback"
    except TypeError as exc:
        assert "strict mode" in str(exc).lower()


def test_runner_env_strict_blocks_legacy_phase_fallback(monkeypatch):
    monkeypatch.setenv("RUNNER_STRICT", "1")
    agent = DummyAgent()
    phase = LegacyOnlyPhase(agent, n_trials=1)
    runner = Runner(phase)
    try:
        runner.run()
        assert False, "Expected RUNNER_STRICT=1 to reject legacy phase fallback"
    except TypeError as exc:
        assert "strict mode" in str(exc).lower()
