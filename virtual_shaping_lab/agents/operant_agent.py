# agents/operant_agent.py

from typing import Optional
import numpy as np

from agents.base import Agent
from agents.representations.observation import Observation


class OperantAgent(Agent):
    """
    Operant agent with explicit policy-based action selection.
    """

    def __init__(self, learner, representation, policy):
        self.learner = learner
        self.representation = representation
        self.policy = policy
        self._state: Optional[np.ndarray] = None

    # -------------------------------------------------
    # Lifecycle
    # -------------------------------------------------

    def reset(self) -> None:
        self._state = None
        if hasattr(self.learner, "reset"):
            self.learner.reset()
        if hasattr(self.representation, "reset"):
            self.representation.reset()
        if hasattr(self.policy, "reset"):
            self.policy.reset()

    # -------------------------------------------------
    # Observation / Encoding
    # -------------------------------------------------

    def observe(self, observation: Observation) -> np.ndarray:
        self._state = self.representation.encode(observation)
        return self._state

    # -------------------------------------------------
    # Prediction
    # -------------------------------------------------

    def value(self, state: np.ndarray, action: Optional[int] = None) -> float:
        return self.learner.value(state, action)

    # -------------------------------------------------
    # Learning update
    # -------------------------------------------------

    def update(
        self,
        state: np.ndarray,
        reward: float,
        action: Optional[int] = None,
        next_state: Optional[np.ndarray] = None,
        done: Optional[bool] = None,
    ) -> None:
        if hasattr(self.learner, "update"):
            try:
                self.learner.update(
                    state,
                    reward,
                    action=action,
                    next_state=next_state,
                    done=done,
                )
            except TypeError:
                # Backward-compatible fallback for legacy learner signatures.
                self.learner.update(state, reward, action)
        else:
            raise AttributeError("Learner does not implement update()")

    # -------------------------------------------------
    # Action selection
    # -------------------------------------------------

    def act(self, state: np.ndarray) -> Optional[int]:
        if self.policy is None:
            return None
        if hasattr(self.policy, "select_action"):
            try:
                return self.policy.select_action(state, value_fn=self.value)
            except TypeError:
                return self.policy.select_action(state)
        return None
