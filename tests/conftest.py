import sys
import os
from pathlib import Path
import pytest


ROOT = Path(__file__).resolve().parents[1]
VSL_ROOT = ROOT / "virtual_shaping_lab"
if str(VSL_ROOT) not in sys.path:
    sys.path.insert(0, str(VSL_ROOT))

os.environ.setdefault("MPLBACKEND", "Agg")


class DummyRepresentation:
    def __init__(self, attention=None):
        self.attention = attention

    def encode(self, observation):
        return observation


class DummyLearner:
    def __init__(self, alpha=0.2):
        self.alpha = alpha
        self.last_update = None

    def update_with_alpha(self, state, reward, action=None, alpha_override=None, delta_override=None):
        self.last_update = {
            "state": state,
            "reward": reward,
            "action": action,
            "alpha_override": alpha_override,
            "delta_override": delta_override,
        }


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

    def act(self, state):
        return None

    def update(self, state, reward, action=None):
        self.last_update = {
            "state": state,
            "reward": reward,
            "action": action,
        }

    def update_with_alpha(self, state, reward, action=None, alpha_override=None, delta_override=None):
        self.learner.update_with_alpha(
            state,
            reward,
            action=action,
            alpha_override=alpha_override,
            delta_override=delta_override,
        )


@pytest.fixture
def dummy_agent():
    return DummyAgent(attention=0.5)
