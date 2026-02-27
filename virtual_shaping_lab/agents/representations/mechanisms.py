from __future__ import annotations

from typing import Any, Dict

import numpy as np

from virtual_shaping_lab.agents.representations.observation import DEFAULT_CONTEXT
from virtual_shaping_lab.agents.representations.observation_encoder import ObservationVectorEncoder
from virtual_shaping_lab.agents.representations.similarity import build_similarity_weights
from virtual_shaping_lab.domain.types import Observation


def apply_salience(vec: np.ndarray, salience: np.ndarray) -> np.ndarray:
    """Apply salience scaling to a feature vector."""
    if salience.shape[0] == vec.shape[0]:
        return vec * salience
    scale = np.ones(vec.shape[0], dtype=float)
    limit = min(salience.shape[0], scale.shape[0])
    scale[:limit] = salience[:limit]
    return vec * scale


def encode_with_mechanisms(
    encoder: ObservationVectorEncoder,
    observation: Observation,
    *,
    similarity_map: Dict[str, Dict[str, float]],
    salience: np.ndarray,
) -> np.ndarray:
    """
    Encode observation using a deterministic mechanism order:
    context namespacing (via encoder), then similarity spread, then salience scaling.
    Attention is learner-owned and intentionally not applied here.
    """
    features = list(observation.stimuli)
    compound = bool(observation.compound)
    context = observation.context if observation.context is not None else DEFAULT_CONTEXT
    weights = build_similarity_weights(features, similarity_map) if similarity_map else None

    vec = np.zeros(encoder.dimension, dtype=float)
    if encoder.mode in {"elemental", "hybrid"}:
        elem_features = list(weights.keys()) if weights is not None else features
        encoder.add_elemental_features(vec, elem_features, context, weights=weights)

    if encoder.mode in {"configural", "hybrid"} and (compound or encoder.mode == "configural"):
        encoder.add_compound_feature(vec, features, context)

    return apply_salience(vec, salience)
