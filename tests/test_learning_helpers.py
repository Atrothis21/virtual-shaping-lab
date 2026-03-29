from experiment.phases.learning_helpers import apply_attention_update
import pytest


class DummyLearner:
    def __init__(self, alpha=0.2):
        self.alpha = alpha
        self.attention_map = {}
        self.last_transition = None


    def attention_multiplier(self, cue_labels):
        if cue_labels is None:
            return 1.0
        if isinstance(cue_labels, (list, tuple)):
            vals = [float(self.attention_map.get(str(c), 1.0)) for c in cue_labels]
            return sum(vals) / len(vals) if vals else 1.0
        return float(self.attention_map.get(str(cue_labels), 1.0))

    def update(self, transition):
        self.last_transition = transition


class DummyAgent:
    def __init__(self, attention_map=None):
        self.representation = object()
        self.learner = DummyLearner(alpha=0.2)
        self.learner.attention_map = dict(attention_map or {})
        self.last_update = None

    def learn(self, transition):
        self.last_update = transition
        self.learner.update(transition)


def test_apply_attention_update_sets_cue_labels_for_attention():
    agent = DummyAgent(attention_map={"tone": 0.5})
    apply_attention_update(agent, state="s", reward=1.0, action=None, cue_labels="tone")
    assert agent.learner.last_transition is not None
    assert agent.learner.last_transition.metadata["cue_labels"] == "tone"


def test_apply_attention_update_falls_back():
    agent = DummyAgent(attention_map=None)
    apply_attention_update(agent, state="s", reward=1.0, action=None)
    assert agent.last_update is not None


def test_apply_attention_update_uses_mean_for_multiple_cues_metadata():
    agent = DummyAgent(attention_map={"tone": 0.4, "noise": 0.8})
    apply_attention_update(agent, state="s", reward=1.0, action=None, cue_labels=["tone", "noise"])
    assert agent.learner.last_transition is not None
    assert agent.learner.last_transition.metadata["cue_labels"] == ["tone", "noise"]


class UpdateOnlyAgent:
    def update(self, *_args, **_kwargs):
        return None


def test_apply_attention_update_rejects_legacy_update_only_dispatch():
    with pytest.raises(AttributeError, match="learn\\(Transition\\)"):
        apply_attention_update(UpdateOnlyAgent(), state="s", reward=1.0, action=None)
