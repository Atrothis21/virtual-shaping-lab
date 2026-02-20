# policies/base.py

"""
Policy definitions.

A Policy:
- Chooses actions based on state (and value estimates)
- Does NOT update values
- Does NOT know about rewards directly
- Does NOT depend on concrete learner classes
"""

from abc import ABC, abstractmethod
from typing import Any, Callable
import numpy as np

ValueFn = Callable[[np.ndarray, Any], float]


class Policy(ABC):
    """
    Abstract base class for all policies.
    """

    @abstractmethod
    def select_action(self, state: np.ndarray, value_fn: ValueFn) -> Any:
        """
        Select an action given the current state.

        Parameters
        ----------
        state : np.ndarray
            Encoded state vector
        value_fn : Callable
            A function that returns value estimates, e.g. learner.value(state, action)

        Returns
        -------
        action : Any
            Action to take
        """
        raise NotImplementedError
