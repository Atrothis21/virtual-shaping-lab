"""Consequence mapper contracts and implementations."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class Consequence:
    reward: float
    event_type: str | None


class ConsequenceMapper(ABC):
    @abstractmethod
    def map(self, *, collected: bool) -> Consequence:
        raise NotImplementedError


class ConstantConsequenceMapper(ConsequenceMapper):
    def __init__(self, reward: float):
        self.reward = float(reward)

    def map(self, *, collected: bool) -> Consequence:
        if collected:
            event_type = "reinforcement" if self.reward > 0 else ("punishment" if self.reward < 0 else "extinction")
            return Consequence(reward=self.reward, event_type=event_type)
        return Consequence(reward=0.0, event_type=None)

