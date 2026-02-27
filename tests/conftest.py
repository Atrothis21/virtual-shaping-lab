import os
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
VSL_ROOT = ROOT / "virtual_shaping_lab"
if str(VSL_ROOT) not in sys.path:
    sys.path.insert(0, str(VSL_ROOT))

os.environ.setdefault("MPLBACKEND", "Agg")

from domain.types import Transition


class DummyRepresentation:
    def __init__(self, attention=None):
        self.attention = attention

    def encode(self, observation):
        return observation


class DummyLearner:
    def __init__(self, alpha=0.2):
        self.alpha = alpha
        self.last_transition = None

    def update(self, transition: Transition):
        self.last_transition = transition


class DummyAgent:
    def __init__(self, attention=None):
        self.representation = DummyRepresentation(attention=attention)
        self.learner = DummyLearner(alpha=0.2)
        self.last_update = None

    def reset(self):
        self.last_update = None

    def observe(self, observation):
        return self.representation.encode(observation)

    def value(self, state, action=None):
        return 0.5

    def act(self, state, actions=None, rng=None):
        return None

    def update(self, state, reward, action=None):
        self.last_update = {
            "state": state,
            "reward": reward,
            "action": action,
        }

    def learn(self, transition: Transition):
        self.last_update = transition
        self.learner.update(transition)


@pytest.fixture
def dummy_agent():
    return DummyAgent(attention=0.5)
