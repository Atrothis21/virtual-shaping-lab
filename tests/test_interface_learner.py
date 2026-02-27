import numpy as np
import pytest

from agents.interfaces import ILearner
from domain.types import EncodedState, Transition


class GoodLearner(ILearner):
    def __init__(self):
        self.last_transition = None

    def reset(self) -> None:
        self.last_transition = None

    def value(self, state: EncodedState, action=None) -> float:
        return float(np.sum(state.x))

    def update(self, transition: Transition) -> None:
        self.last_transition = transition


class MissingUpdate(ILearner):
    def reset(self) -> None:
        return None

    def value(self, state: EncodedState, action=None) -> float:
        return 0.0


def test_learner_interface_happy_path():
    learner = GoodLearner()
    state = EncodedState(x=np.asarray([1.0, 2.0], dtype=float))
    transition = Transition(s=state, r=1.0)

    assert learner.value(state) == 3.0
    learner.update(transition)
    assert learner.last_transition is transition


def test_learner_interface_requires_update():
    with pytest.raises(TypeError):
        MissingUpdate()

