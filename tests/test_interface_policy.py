import numpy as np
import pytest

from agents.interfaces import IPolicy
from domain.types import EncodedState


class GoodPolicy(IPolicy):
    def reset(self) -> None:
        return None

    def select_action(self, state, actions, value_fn, rng):
        return actions[0] if actions else None


class MissingSelectAction(IPolicy):
    def reset(self) -> None:
        return None


def test_policy_interface_happy_path():
    policy = GoodPolicy()
    state = EncodedState(x=np.asarray([1.0], dtype=float))

    def value_fn(s, action):
        return 1.0

    action = policy.select_action(
        state=state,
        actions=["left", "right"],
        value_fn=value_fn,
        rng=np.random.default_rng(7),
    )
    assert action == "left"


def test_policy_interface_requires_select_action():
    with pytest.raises(TypeError):
        MissingSelectAction()

