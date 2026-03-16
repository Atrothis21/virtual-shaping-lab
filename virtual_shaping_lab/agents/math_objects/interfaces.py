"""Mathematical-object interface contracts for V2 mechanism formalization.

Each interface declares an explicit mapping from a domain to a codomain so
representation, learning, and control mechanisms can be reasoned about as
first-class mathematical objects instead of ad hoc helpers.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Mapping, Sequence

import numpy as np


class IContextMap(ABC):
    """Context map contract.

    Domain/codomain:
    - maps `(observation, context)` to a context-conditioned observation-like value
    - formal shape: `C : O x K -> O_c`
    """

    @abstractmethod
    def apply(self, observation: Any, context: Any) -> Any:
        raise NotImplementedError


class ISimilarityKernel(ABC):
    """Similarity kernel contract.

    Domain/codomain:
    - maps a pair of encoded feature labels or states to a scalar similarity weight
    - formal shape: `S : X x X -> R`
    """

    @abstractmethod
    def similarity(self, left: Any, right: Any) -> float:
        raise NotImplementedError


class ISalienceOperator(ABC):
    """Salience operator contract.

    Domain/codomain:
    - maps an input feature vector to a salience-scaled feature vector
    - formal shape: `Sigma : X -> X`
    """

    @abstractmethod
    def apply(self, vector: np.ndarray) -> np.ndarray:
        raise NotImplementedError


class ITemporalBasis(ABC):
    """Temporal basis contract.

    Domain/codomain:
    - maps scalar or structured time input to a fixed-dimensional temporal basis vector
    - formal shape: `T : Time -> R^d_t`
    """

    @abstractmethod
    def encode(self, t_s: float, dt_s: float | None = None) -> np.ndarray:
        raise NotImplementedError


class IPredictionErrorRule(ABC):
    """Prediction-error rule contract.

    Domain/codomain:
    - maps `(x_t, r_t, x_{t+1}, theta_t, metadata)` to a scalar prediction error
    - formal shape: `delta : (X_t, R_t, X_{t+1}, Theta_t) -> R`
    """

    @abstractmethod
    def compute(
        self,
        *,
        state: np.ndarray,
        reward: float,
        next_state: np.ndarray | None = None,
        parameters: Any = None,
        metadata: Mapping[str, Any] | None = None,
    ) -> float:
        raise NotImplementedError


class IAttentionMechanism(ABC):
    """Attention mechanism contract.

    Domain/codomain:
    - maps current sufficient statistics and mechanism state to the next attention state
    - formal shape: `A_{t+1} = G(A_t, x_t, r_t, y_hat_t, cuewise_stats)`
    """

    @abstractmethod
    def current_alpha(self, active_features: Sequence[str]) -> Mapping[str, float]:
        raise NotImplementedError

    @abstractmethod
    def update_state(self, context: Any) -> None:
        raise NotImplementedError


