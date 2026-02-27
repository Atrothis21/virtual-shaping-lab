import numpy as np
import pytest

from agents.interfaces import IRepresentation
from domain.types import EncodedState, Observation


class GoodRepresentation(IRepresentation):
    def reset(self) -> None:
        return None

    def encode(self, observation: Observation) -> EncodedState:
        return EncodedState(x=np.asarray([1.0, 0.0], dtype=float), key="ok")


class MissingEncode(IRepresentation):
    def reset(self) -> None:
        return None


def test_representation_interface_happy_path():
    rep = GoodRepresentation()
    state = rep.encode(Observation(stimuli=["tone"], context="A"))

    assert isinstance(state, EncodedState)
    assert state.key == "ok"
    assert state.x.shape == (2,)


def test_representation_interface_requires_encode():
    with pytest.raises(TypeError):
        MissingEncode()

