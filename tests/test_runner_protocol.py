from typing import Any, Dict, List

from experiment.runner import Runner
from experiment.phases.base import PhaseBase
from protocols.base import BaseProtocol


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
