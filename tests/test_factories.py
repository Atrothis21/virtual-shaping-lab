import pytest

from experiment.factories.agent_factory import build_agent, validate_agent
from experiment.factories.learner_factory import build_learner, validate_learner
from experiment.factories.policy_factory import build_policy, validate_policy
from experiment.factories.representation_factory import build_representation, validate_representation
from experiment.factories import learner_factory
from experiment.factories import phase_factory
from experiment.factories import policy_factory
from experiment.factories import protocol_factory
from experiment.factories import representation_factory
from experiment.factories import reward_schedule_factory


def test_validate_agent_rejects_unknown():
    with pytest.raises(KeyError):
        validate_agent("unknown_agent")


def test_build_learner_smoke():
    learner = build_learner("rescorla_wagner", state_dim=4, alpha=0.2, gamma=0.0)
    assert learner is not None


def test_validate_policy_rejects_unknown():
    with pytest.raises(KeyError):
        validate_policy("unknown_policy")


def test_build_policy_smoke():
    policy = build_policy("fixed", action=0)
    assert policy is not None


def test_build_representation_smoke():
    rep = build_representation(
        "vector_elemental",
        stimuli=["tone", "noise"],
        max_compound_size=2,
    )
    assert rep is not None


class DummyLearner:
    def __init__(self, **kwargs):
        self.kwargs = kwargs


class DummyPhase:
    def __init__(self, **kwargs):
        self.kwargs = kwargs


class DummyProtocol:
    def __init__(self, **kwargs):
        self.kwargs = kwargs


class DummyRepresentation:
    def __init__(self, params=None):
        self.params = params or {}


def test_learner_factory_unknown_and_build(monkeypatch):
    monkeypatch.setattr(learner_factory, "LEARNER_REGISTRY", {"dummy": DummyLearner})
    with pytest.raises(KeyError):
        learner_factory.validate_learner("missing")
    inst = learner_factory.build_learner("dummy", alpha=0.1)
    assert isinstance(inst, DummyLearner)
    assert inst.kwargs["alpha"] == 0.1


def test_phase_factory_branches(monkeypatch):
    monkeypatch.setattr(phase_factory, "PHASE_REGISTRY", {"dummy": DummyPhase})
    with pytest.raises(KeyError):
        phase_factory.validate_phase("missing")

    inst = phase_factory.build_phase("dummy", agent="agent")
    assert inst.kwargs == {"agent": "agent", "params": {}}

    inst = phase_factory.build_phase("dummy", agent="agent", n_trials=5)
    assert inst.kwargs == {"agent": "agent", "n_trials": 5, "params": {}}

    inst = phase_factory.build_phase("dummy", agent="agent", stimuli=["tone"])
    assert inst.kwargs == {"agent": "agent", "stimuli": ["tone"], "params": {}}

    inst = phase_factory.build_phase("dummy", agent="agent", stimuli=["tone"], n_trials=3)
    assert inst.kwargs == {"agent": "agent", "stimuli": ["tone"], "n_trials": 3, "params": {}}


def test_policy_factory_unknown_and_build(monkeypatch):
    monkeypatch.setattr(policy_factory, "POLICY_REGISTRY", {"dummy": lambda **params: params})
    with pytest.raises(KeyError):
        policy_factory.validate_policy("missing")
    inst = policy_factory.build_policy("dummy", epsilon=0.2)
    assert inst["epsilon"] == 0.2


def test_protocol_factory_unknown_and_build(monkeypatch):
    monkeypatch.setattr(protocol_factory, "PROTOCOL_REGISTRY", {"dummy": DummyProtocol})
    with pytest.raises(KeyError):
        protocol_factory.validate_protocol("missing")
    inst = protocol_factory.build_protocol("dummy", agent="agent", stimuli={"cs_plus": ["tone"]})
    assert inst.kwargs["agent"] == "agent"
    assert inst.kwargs["stimuli"] == {"cs_plus": ["tone"]}
    assert inst.kwargs["params"] == {}


def test_representation_factory_unknown_and_build(monkeypatch):
    monkeypatch.setattr(representation_factory, "REPRESENTATION_REGISTRY", {"dummy": DummyRepresentation})
    with pytest.raises(KeyError):
        representation_factory.validate_representation("missing")
    inst = representation_factory.build_representation("dummy", foo="bar")
    assert isinstance(inst, DummyRepresentation)
    assert inst.params["foo"] == "bar"


def test_reward_schedule_factory_branches(monkeypatch):
    with pytest.raises(TypeError):
        reward_schedule_factory.build_reward_schedule("not-a-dict")

    with pytest.raises(KeyError):
        reward_schedule_factory.build_reward_schedule({})

    with pytest.raises(KeyError):
        reward_schedule_factory.build_reward_schedule({"type": "fixed_ratio"})

    with pytest.raises(KeyError):
        reward_schedule_factory.validate_reward_schedule("missing")

    class DummySchedule:
        def __init__(self, **kwargs):
            self.kwargs = kwargs

    monkeypatch.setattr(
        reward_schedule_factory,
        "REWARD_SCHEDULE_REGISTRY",
        {
            "fixed_ratio": DummySchedule,
            "variable_ratio": DummySchedule,
            "fixed_interval": DummySchedule,
            "variable_interval": DummySchedule,
            "other": DummySchedule,
        },
    )

    fixed = reward_schedule_factory.build_reward_schedule({"type": "fixed_ratio", "value": 2})
    assert fixed.kwargs["n"] == 2
    assert fixed.kwargs["reward"] == 1.0

    vr = reward_schedule_factory.build_reward_schedule({"type": "variable_ratio", "value": 5})
    assert vr.kwargs["mean_n"] == 5
    assert vr.kwargs["reward"] == 1.0

    fi = reward_schedule_factory.build_reward_schedule({"type": "fixed_interval", "value": 7})
    assert fi.kwargs["interval"] == 7
    assert fi.kwargs["reward"] == 1.0

    vi = reward_schedule_factory.build_reward_schedule({"type": "variable_interval", "value": 9})
    assert vi.kwargs["mean_interval"] == 9
    assert vi.kwargs["reward"] == 1.0

    fixed_neg = reward_schedule_factory.build_reward_schedule({"type": "fixed_ratio", "value": 2, "reward": -0.5})
    assert fixed_neg.kwargs["reward"] == -0.5

    with pytest.raises(RuntimeError):
        reward_schedule_factory.build_reward_schedule({"type": "other", "value": 1})
