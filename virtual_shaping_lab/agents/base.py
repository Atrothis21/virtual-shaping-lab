# agents/base.py

from abc import ABC, abstractmethod
from typing import Optional, Any
import inspect
import numpy as np
from virtual_shaping_lab.agents.representations.observation import Observation


class Agent(ABC):
    """
    Base class for all agents.

    Architecture:
      - Agent assembles learner + policy
      - Learner does not know policy
      - Policy does not know learner (only uses value_fn callbacks)

    Vector-first contract:
        - observe() returns a numpy vector (state)
        - value() consumes a numpy vector
        - update() consumes a numpy vector
    """

    # -------------------------------------------------
    # Lifecycle
    # -------------------------------------------------

    @abstractmethod
    def reset(self) -> None:
        """
        Reset the agent's internal state.

        Called at the start of each experiment run.
        """
        pass

    # -------------------------------------------------
    # Observation / Encoding
    # -------------------------------------------------

    @abstractmethod
    def observe(self, observation: Observation) -> np.ndarray:
        """
        Observe a raw stimulus or observation and encode it.

        This should call Representation.encode(...) and store
        the encoded state internally (e.g., self._state).

        Returns
        -------
        np.ndarray
            Encoded state vector.
        """
        pass

    # -------------------------------------------------
    # Learning
    # -------------------------------------------------

    @abstractmethod
    def update(
        self,
        state: np.ndarray,
        reward: float,
        action: Optional[int] = None
    ) -> None:
        """
        Update internal state using a reinforcement signal.

        Parameters
        ----------
        state : np.ndarray
            Encoded state vector
        reward : float
            Reinforcement signal
        action : int, optional
            Action taken (only relevant for operant agents)
        """
        pass

    # -------------------------------------------------
    # Prediction (CANONICAL API)
    # -------------------------------------------------

    @abstractmethod
    def value(self, state: np.ndarray, action: Optional[int] = None) -> float:
        """
        Return the agent's current value prediction for a state.

        In classical conditioning, this corresponds to:
        - associative strength
        - expected outcome
        """
        pass

    # -------------------------------------------------
    # Action selection (policy-mediated)
    # -------------------------------------------------

    def act(self, state: np.ndarray) -> Optional[int]:
        """
        Select an action given the current state.

        Uses self.policy if present; otherwise returns None.

        This keeps learners independent of policies.
        """
        policy = getattr(self, "policy", None)
        if policy is None:
            return None

        # Preferred: policy.select_action(state, value_fn=...)
        if hasattr(policy, "select_action"):
            sig = inspect.signature(policy.select_action)
            params = list(sig.parameters.values())
            if params and params[0].name == "self":
                params = params[1:]
            if len(params) >= 2:
                return policy.select_action(state, value_fn=self.value)
            return policy.select_action(state)

        return None

    def update_with_alpha(
        self,
        state: np.ndarray,
        reward: float,
        action: Optional[int] = None,
        alpha_override: Optional[Any] = None,
        delta_override: Optional[float] = None,
    ) -> None:
        """
        Optional cue-specific learning update.
        Falls back to update() if learner does not support it.
        """
        learner = getattr(self, "learner", None)
        if learner is not None and hasattr(learner, "update_with_alpha"):
            learner.update_with_alpha(
                state,
                reward,
                action=action,
                alpha_override=alpha_override,
                delta_override=delta_override,
            )
            return

        self.update(state, reward, action)


