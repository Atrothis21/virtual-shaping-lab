# agents/classical_agent.py

from typing import Optional
import numpy as np

from agents.base import Agent
from agents.representations.observation import Observation


class ClassicalAgent(Agent):
    """
    Classical (Pavlovian) agent.

    Learns associative strength via the learner (e.g., Rescorla-Wagner).
    Does not select actions (act returns None).
    """

    def __init__(self, learner, representation):
        self.learner = learner
        self.representation = representation
        self._state: Optional[np.ndarray] = None

    # -------------------------------------------------
    # Lifecycle
    # -------------------------------------------------

    def reset(self) -> None:
        """
        Reset internal agent and learner state.
        """
        self._state = None
        if hasattr(self.learner, "reset"):
            self.learner.reset()
        if hasattr(self.representation, "reset"):
            self.representation.reset()

    # -------------------------------------------------
    # Observation / Encoding (Agent contract)
    # -------------------------------------------------

    def observe(self, observation: Observation) -> np.ndarray:
        """
        Observe a raw stimulus/observation and cache its encoded state.
        """
        self._state = self.representation.encode(observation)
        return self._state

    # -------------------------------------------------
    # Prediction (Agent contract)
    # -------------------------------------------------

    def value(self, state: np.ndarray, action: Optional[int] = None) -> float:
        """
        Return the agent's current value prediction for a state.
        """
        return self.learner.value(state, action)

    # -------------------------------------------------
    # Learning update (Agent contract)
    # -------------------------------------------------

    def update(
        self,
        state: np.ndarray,
        reward: float,
        action: Optional[int] = None
    ) -> None:
        """
        Update the learner given a state and reward.
        """
        if hasattr(self.learner, "update"):
            self.learner.update(state, reward, action)
        else:
            raise AttributeError("Learner does not implement update()")

    def act(self, state: np.ndarray) -> Optional[int]:
        """
        Classical agents do not select actions.
        """
        return None
