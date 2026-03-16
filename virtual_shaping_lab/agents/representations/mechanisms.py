from __future__ import annotations

from typing import Any, Dict

import numpy as np

from virtual_shaping_lab.agents.math_objects.interfaces import IContextMap, ISalienceOperator, ISimilarityKernel
from virtual_shaping_lab.agents.representations.observation import DEFAULT_CONTEXT
from virtual_shaping_lab.agents.representations.observation_encoder import ObservationVectorEncoder
from virtual_shaping_lab.agents.representations.similarity import build_similarity_weights
from virtual_shaping_lab.domain.types import Observation

def encode_with_mechanisms(
    encoder: ObservationVectorEncoder,
    observation: Observation,
    *,
    similarity_map: Dict[str, Dict[str, float]],
    salience: np.ndarray,
    context_map: IContextMap | None = None,
    similarity_kernel: ISimilarityKernel | None = None,
    salience_operator: ISalienceOperator | None = None,
) -> np.ndarray:
    """
    Encode observation using a deterministic mechanism order:
    context namespacing (via encoder), then similarity spread, then salience scaling.
    Attention is learner-owned and intentionally not applied here.
    """
    normalized_observation = (
        context_map.apply(observation, observation.context)
        if context_map is not None
        else observation
    )
    features = list(normalized_observation.stimuli)
    compound = bool(normalized_observation.compound)
    context = normalized_observation.context if normalized_observation.context is not None else DEFAULT_CONTEXT
    if similarity_kernel is not None and hasattr(similarity_kernel, "spread_weights"):
        weights = similarity_kernel.spread_weights(features)
    else:
        weights = build_similarity_weights(features, similarity_map) if similarity_map else None

    vec = np.zeros(encoder.dimension, dtype=float)
    if encoder.mode in {"elemental", "hybrid"}:
        elem_features = list(weights.keys()) if weights is not None else features
        encoder.add_elemental_features(vec, elem_features, context, weights=weights)

    if encoder.mode in {"configural", "hybrid"} and (compound or encoder.mode == "configural"):
        encoder.add_compound_feature(vec, features, context)

    if salience_operator is not None:
        return salience_operator.apply(vec)

    scale = np.ones(vec.shape[0], dtype=float)
    limit = min(salience.shape[0], scale.shape[0])
    scale[:limit] = salience[:limit]
    return vec * scale
