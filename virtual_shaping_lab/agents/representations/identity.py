"""Identity representation implementation aligned to v2 contracts."""

from __future__ import annotations

from typing import Any, Dict, Optional

import numpy as np

from virtual_shaping_lab.agents.representations.base import RepresentationBase
from virtual_shaping_lab.domain.types import EncodedState, Observation


class IdentityRepresentation(RepresentationBase):
    """
    Pass-through vector representation.

    Expects `Observation.metadata["vector"]` to contain a 1-D numeric vector.
    """

    name = "identity"

    def __init__(self, params: Optional[Dict[str, Any]] = None):
        super().__init__(params=params)
        self._dimension = self.params.get("dimension")

    def encode(self, observation: Observation) -> EncodedState:
        vec = np.asarray(observation.metadata.get("vector"), dtype=float)
        if vec.ndim != 1:
            raise ValueError("IdentityRepresentation expects a 1-D vector in observation.metadata['vector'].")
        if self._dimension is not None and vec.size != int(self._dimension):
            raise ValueError(f"Expected vector dimension {int(self._dimension)}, got {vec.size}.")
        if self._dimension is None:
            self._dimension = int(vec.size)
        return EncodedState(x=vec)

    @property
    def dimension(self) -> int:
        if self._dimension is None:
            raise ValueError("IdentityRepresentation dimension is undefined before first encode().")
        return int(self._dimension)

