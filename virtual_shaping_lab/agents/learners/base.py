# learners/base.py

"""
Base learner definitions.

A Learner:
- Owns learnable parameters (e.g. weights)
- Receives transitions
- Updates its parameters according to a learning rule

Vector-first contract:
- state is always a numpy vector
"""

from abc import ABC, abstractmethod
from typing import Dict, Optional
import numpy as np


class BaseLearner(ABC):
    """
    Abstract base class for all learning algorithms.

    BaseLearner is intentionally minimal:
    - RW / TD-value are valid
    - Operant learners can extend it
    """

    # Metadata for UI/validation/routing
    learner_type: str = "pavlovian"  # "pavlovian" | "operant" | "both"

    def __init__(self, alpha: float, gamma: float):
        """
        Parameters
        ----------
        alpha : float
            Learning rate
        gamma : float
            Discount factor
        """
        self.alpha = alpha
        self.gamma = gamma

    # -------------------------------------------------
    # Required hooks
    # -------------------------------------------------

    @abstractmethod
    def update(
        self,
        state: np.ndarray,
        reward: float,
        action: Optional[int] = None,
        next_state: Optional[np.ndarray] = None,
        done: Optional[bool] = None
    ) -> None:
        """
        Update learner parameters from a transition.

        Parameters
        ----------
        state : np.ndarray
            Encoded state vector
        reward : float
            Reinforcement signal
        action : int, optional
            Action taken (for operant learners)
        next_state : np.ndarray, optional
            Next state vector (for TD learners)
        done : bool, optional
            Episode termination flag
        """
        raise NotImplementedError

    def update_with_alpha(
        self,
        state,
        reward,
        action=None,
        alpha_override=None,
        delta_override=None
    ):
        """
        Optional cue-specific learning update.
        """
        return self.update(state, reward, action)

    @abstractmethod
    def value(self, state: np.ndarray, action: Optional[int] = None) -> float:
        """
        Return the value estimate for a state or state-action pair.

        Parameters
        ----------
        state : np.ndarray
            Encoded state vector
        action : int, optional
            Action (for Q-learners)

        Returns
        -------
        float
            Estimated value
        """
        raise NotImplementedError

    # -------------------------------------------------
    # Optional hooks
    # -------------------------------------------------

    def expects_action(self) -> bool:
        """
        Whether this learner requires an action for update/value.

        Used for validation/routing only.
        """
        return False

    def start_episode(self) -> None:
        """
        Hook called at the beginning of an episode.
        """
        pass

    def end_episode(self) -> None:
        """
        Hook called at the end of an episode.
        """
        pass

    def get_parameters(self) -> Dict[str, np.ndarray]:
        """
        Return learnable parameters for analysis or visualization.
        """
        return {}


class OperantLearner(BaseLearner, ABC):
    """
    Abstract base for operant learners.

    Operant learners require actions for learning.
    """

    learner_type: str = "operant"

    def expects_action(self) -> bool:
        return True
