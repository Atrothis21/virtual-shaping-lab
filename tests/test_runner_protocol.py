from typing import Any, Dict, List

from experiment.runner import Runner
from experiment.phases.base import PhaseBase
from experiment.domain.types import StepResult
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
