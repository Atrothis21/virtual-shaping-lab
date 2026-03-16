"""Mathematical object contracts for the V2 cognitive architecture."""

from .interfaces import (
    IAttentionMechanism,
    IContextMap,
    IPredictionErrorRule,
    ISalienceOperator,
    ISimilarityKernel,
    ITemporalBasis,
)
from .representation_objects import DefaultContextMap, MatrixSimilarityKernel
from .salience_objects import DiagonalSalienceOperator
from .temporal_objects import (
    BinnedTemporalBasis,
    IdentityTemporalBasis,
    TraceTemporalBasis,
    build_temporal_basis,
)

__all__ = [
    "IAttentionMechanism",
    "IContextMap",
    "IPredictionErrorRule",
    "ISalienceOperator",
    "ISimilarityKernel",
    "ITemporalBasis",
    "DefaultContextMap",
    "MatrixSimilarityKernel",
    "DiagonalSalienceOperator",
    "IdentityTemporalBasis",
    "BinnedTemporalBasis",
    "TraceTemporalBasis",
    "build_temporal_basis",
]
