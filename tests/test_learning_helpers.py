from experiment.phases.learning_helpers import apply_attention_update
import pytest


class DummyLearner:
    def __init__(self, alpha=0.2):
        self.alpha = alpha
        self.attention_map = {}
        self.last_update = None

    def update_with_alpha(self, state, reward, action=None, alpha_override=None, delta_override=None):
        self.last_update = {
            "state": state,
            "reward": reward,
            "action": action,
            "alpha_override": alpha_override,
            "delta_override": delta_override,
        }


    def attention_multiplier(self, cue_labels):
        if cue_labels is None:
            return 1.0
        if isinstance(cue_labels, (list, tuple)):
            vals = [float(self.attention_map.get(str(c), 1.0)) for c in cue_labels]
            return sum(vals) / len(vals) if vals else 1.0
        return float(self.attention_map.get(str(cue_labels), 1.0))


class DummyAgent:
    def __init__(self, attention_map=None):
        self.representation = object()
        self.learner = DummyLearner(alpha=0.2)
        self.learner.attention_map = dict(attention_map or {})
        self.last_update = None

    def update(self, state, reward, action=None):
        self.last_update = {"state": state, "reward": reward, "action": action}

    def update_with_alpha(self, state, reward, action=None, alpha_override=None, delta_override=None):
        self.learner.update_with_alpha(
            state,
            reward,
            action=action,
            alpha_override=alpha_override,
            delta_override=delta_override,
        )


def test_apply_attention_update_uses_override():
    agent = DummyAgent(attention_map={"tone": 0.5})
    apply_attention_update(agent, state="s", reward=1.0, action=None, cue_labels="tone")
    assert agent.learner.last_update is not None
    assert agent.learner.last_update["alpha_override"] == 0.5 * agent.learner.alpha


def test_apply_attention_update_falls_back():
    agent = DummyAgent(attention_map=None)
    apply_attention_update(agent, state="s", reward=1.0, action=None)
    assert agent.last_update is not None


def test_apply_attention_update_uses_mean_for_multiple_cues():
    agent = DummyAgent(attention_map={"tone": 0.4, "noise": 0.8})
    apply_attention_update(agent, state="s", reward=1.0, action=None, cue_labels=["tone", "noise"])
    assert agent.learner.last_update is not None
    assert agent.learner.last_update["alpha_override"] == pytest.approx(0.6 * agent.learner.alpha)
