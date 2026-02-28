from __future__ import annotations

from typing import Any, Dict, List

import numpy as np

from experiment.phases.base import PhaseBase
from experiment.runner import Runner
from protocols.base import BaseProtocol
from virtual_shaping_lab.experiment.domain.adapters import PhaseUnitAdapter, ProtocolUnitAdapter
from virtual_shaping_lab.experiment.domain.types import ExperimentContext


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


def _ctx(agent: Any) -> ExperimentContext:
    return ExperimentContext(agent=agent, rng=np.random.default_rng(123))


def test_phase_adapter_preserves_runner_records():
    agent = DummyAgent()
    phase = DummyPhase(agent=agent, n_trials=2)
    expected = Runner(phase).run()

    phase2 = DummyPhase(agent=agent, n_trials=2)
    adapter = PhaseUnitAdapter(phase2)
    steps = list(adapter.iter_steps(_ctx(agent)))
    got = [s.metadata["record"] for s in steps]

    assert got == expected
    assert steps[-1].done is True


def test_protocol_adapter_preserves_runner_records():
    agent = DummyAgent()
    protocol = DummyProtocol(agent=agent)
    expected = Runner(protocol).run()

    protocol2 = DummyProtocol(agent=agent)
    adapter = ProtocolUnitAdapter(protocol2)
    steps = list(adapter.iter_steps(_ctx(agent)))
    got = [s.metadata["record"] for s in steps]

    assert got == expected
    assert steps[-1].done is True

