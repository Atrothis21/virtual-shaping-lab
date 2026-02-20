# representations/base.py

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
import numpy as np


class RepresentationBase(ABC):
    """
    Base class for all representations.

    Immutable design decision:
        - Representations must encode observations into vectors (or matrices).
        - Learners consume numeric tensors via linear algebra.
        - Non-vector representations are legacy-only and should not be added.

    Representations DO:
        - encode observations into state vectors
        - define state dimensionality
        - manage representation-specific reset behavior

    Representations do NOT:
        - define learning rules
        - define trial logic
        - own action-selection policy
    """

    # ---- Representation metadata (override in subclasses) ----
    name: str = "base"

    def __init__(self, params: Optional[Dict[str, Any]] = None):
        self.params = params or {}

    # ------------------------------------------------------------------
    # Required hooks
    # ------------------------------------------------------------------

    @abstractmethod
    def encode(self, observation: Any) -> np.ndarray:
        """
        Convert a raw observation into an encoded vector.

        Returns
        -------
        np.ndarray
            1-D numeric vector representation.
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def dimension(self) -> int:
        """
        Dimensionality of the encoded vector.

        Returns
        -------
        int
            The fixed feature dimension of the representation.
        """
        raise NotImplementedError

    # ------------------------------------------------------------------
    # Optional hooks
    # ------------------------------------------------------------------

    def reset(self) -> None:
        """
        Reset any internal representation state.
        Default: no-op.
        """
        return None

    def get_summary(self) -> Dict[str, Any]:
        """
        Optional representation-level summary statistics.
        """
        return {}
