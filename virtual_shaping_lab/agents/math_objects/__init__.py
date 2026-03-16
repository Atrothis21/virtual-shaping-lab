"""Mathematical object contracts for the V2 cognitive architecture."""

from .interfaces import (
    IAttentionMechanism,
    IContextMap,
    IPredictionErrorRule,
    ISalienceOperator,
    ISimilarityKernel,
    ITemporalBasis,
)

__all__ = [
    "IAttentionMechanism",
    "IContextMap",
    "IPredictionErrorRule",
    "ISalienceOperator",
    "ISimilarityKernel",
    "ITemporalBasis",
]
