"""Concrete salience operators for representation-time scaling."""

from __future__ import annotations

import numpy as np

from virtual_shaping_lab.agents.math_objects.interfaces import ISalienceOperator


class DiagonalSalienceOperator(ISalienceOperator):
    """Diagonal salience scaling operator.

    Domain/codomain:
    - maps an input feature vector to a salience-scaled feature vector
    - formal shape: `Sigma : X -> X`
    """

    def __init__(self, salience: np.ndarray):
        self.salience = np.asarray(salience, dtype=float)

    def apply(self, vector: np.ndarray) -> np.ndarray:
        vec = np.asarray(vector, dtype=float)
        if self.salience.shape[0] == vec.shape[0]:
            return vec * self.salience
        scale = np.ones(vec.shape[0], dtype=float)
        limit = min(self.salience.shape[0], scale.shape[0])
        scale[:limit] = self.salience[:limit]
        return vec * scale
