from experiment.phases.learning_helpers import apply_attention_update


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


class DummyRepresentation:
    def __init__(self, attention=None):
        self.attention = attention


class DummyAgent:
    def __init__(self, attention=None):
        self.representation = DummyRepresentation(attention=attention)
        self.learner = DummyLearner(alpha=0.2)
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
    agent = DummyAgent(attention=0.5)
    apply_attention_update(agent, state="s", reward=1.0, action=None)
    assert agent.learner.last_update is not None
    assert agent.learner.last_update["alpha_override"] == 0.5 * agent.learner.alpha


def test_apply_attention_update_falls_back():
    agent = DummyAgent(attention=None)
    apply_attention_update(agent, state="s", reward=1.0, action=None)
    assert agent.last_update is not None
