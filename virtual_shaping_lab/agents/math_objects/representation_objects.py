"""Concrete representation-layer mathematical objects."""

from __future__ import annotations

from dataclasses import replace
from typing import Any, Iterable

from virtual_shaping_lab.agents.math_objects.interfaces import IContextMap, ISimilarityKernel
from virtual_shaping_lab.agents.representations.observation import DEFAULT_CONTEXT
from virtual_shaping_lab.domain.types import Observation


class DefaultContextMap(IContextMap):
    """Normalize observations onto a declared context domain.

    Domain/codomain:
    - maps `(observation, context)` to an observation with an explicit context label
    - formal shape: `C : O x K -> O_c`
    """

    def __init__(self, default_context: Any = DEFAULT_CONTEXT):
        self.default_context = default_context

    def apply(self, observation: Observation, context: Any) -> Observation:
        normalized_context = self.default_context if context is None else context
        return replace(observation, context=normalized_context)


class MatrixSimilarityKernel(ISimilarityKernel):
    """Matrix-backed similarity kernel.

    Domain/codomain:
    - maps a pair of feature labels to a scalar weight in `[0, 1]`
    - formal shape: `S : X x X -> R`
    """

    def __init__(self, similarity_map: dict[str, dict[str, float]] | None = None):
        self.similarity_map = similarity_map or {}

    def similarity(self, left: Any, right: Any) -> float:
        if str(left) == str(right):
            return 1.0
        raw = self.similarity_map.get(str(left), {}).get(str(right), 0.0)
        try:
            value = float(raw)
        except (TypeError, ValueError):
            return 0.0
        if value < 0.0:
            return 0.0
        if value > 1.0:
            return 1.0
        return value

    def spread_weights(self, present: Iterable[str]) -> dict[str, float]:
        """Build max-aggregated similarity weights for a presented feature set."""
        weights: dict[str, float] = {str(s): 1.0 for s in present}
        for stim in present:
            stim_key = str(stim)
            for other, raw in self.similarity_map.get(stim_key, {}).items():
                try:
                    weight = float(raw)
                except (TypeError, ValueError):
                    continue
                if weight < 0.0:
                    weight = 0.0
                if weight > 1.0:
                    weight = 1.0
                weights[str(other)] = max(weights.get(str(other), 0.0), weight)
        return weights
