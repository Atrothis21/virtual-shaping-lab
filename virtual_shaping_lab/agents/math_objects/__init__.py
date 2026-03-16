"""Mathematical object contracts for the V2 cognitive architecture.

Concrete implementations live in sibling modules and should be imported from
those modules directly to avoid unnecessary package-level import coupling.
"""

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
