# representations/vector_hybrid.py

from typing import Any, Dict, Optional
import numpy as np

from agents.representations.base import RepresentationBase
from agents.representations.observation import Observation, DEFAULT_CONTEXT
from agents.representations.observation_encoder import ObservationVectorEncoder
from agents.representations.vocab import (
    build_feature_vocab,
    build_feature_weight_vector,
)
from agents.representations.similarity import (
    parse_similarity_matrix,
    build_similarity_weights,
)


class VectorHybridRepresentation(RepresentationBase):
    """
    Hybrid vector representation:
    compounds are encoded as both elemental and configural features.

    Supports two-component encoding:
      - global:<stimulus> and global:compound:<...>
      - ctx:<context>|<stimulus> and ctx:<context>|compound:<...>
    """

    name = "vector_hybrid"

    def _apply_salience(self, vec: np.ndarray) -> np.ndarray:
        if self.salience.shape[0] == vec.shape[0]:
            return vec * self.salience
        scale = np.ones(vec.shape[0], dtype=float)
        limit = min(self.salience.shape[0], scale.shape[0])
        scale[:limit] = self.salience[:limit]
        return vec * scale

    def __init__(self, params: Optional[Dict[str, Any]] = None):
        super().__init__(params=params)

        stimuli = self.params.get("stimuli")
        if not stimuli:
            raise ValueError("vector_hybrid requires params['stimuli']")

        salience = self.params.get("salience", {})
        attention = self.params.get("attention", {})
        similarity = self.params.get("similarity")
        attention_compound = self.params.get("attention_compound", "mean")
        compound_prefix = self.params.get("compound_prefix", "compound:")
        max_compound_size = self.params.get("max_compound_size", 2)

        contexts = self.params.get("contexts")
        context_prefix = self.params.get("context_prefix", "ctx:")
        global_prefix = self.params.get("global_prefix", "global:")

        include_global = self.params.get("include_global", True)
        include_context = self.params.get("include_context", True)

        features, salience_vector = build_feature_vocab(
            stimuli=stimuli,
            include_compounds=True,
            compound_prefix=compound_prefix,
            max_compound_size=max_compound_size,
            contexts=contexts,
            context_prefix=context_prefix,
            global_prefix=global_prefix,
            include_global=include_global,
            include_context=include_context,
            salience=salience,
        )

        self._encoder = ObservationVectorEncoder(
            feature_vocab=features,
            mode="hybrid",
            compound_prefix=compound_prefix,
            context_prefix=context_prefix,
            global_prefix=global_prefix,
            include_global=include_global,
            include_context=include_context,
        )

        self.salience = np.asarray(salience_vector, dtype=float)
        self.attention_map = dict(attention) if attention else {}
        self.similarity_map = parse_similarity_matrix(similarity, stimuli) if similarity else {}
        if attention:
            attention_vector = build_feature_weight_vector(
                features=features,
                weights=attention,
                compound_rule=attention_compound,
                context_prefix=context_prefix,
                global_prefix=global_prefix,
                compound_prefix=compound_prefix,
            )
            self.attention = np.asarray(attention_vector, dtype=float)
        else:
            self.attention = None

    def encode(self, observation: Observation) -> np.ndarray:
        if not self.similarity_map:
            return self._apply_salience(self._encoder.encode(observation))

        features = observation.get("stimuli", [])
        compound = observation.get("compound", False)
        context = observation.get("context", DEFAULT_CONTEXT)

        vec = np.zeros(self.dimension, dtype=float)

        if self._encoder.mode in {"elemental", "hybrid"}:
            weights = build_similarity_weights(features, self.similarity_map)
            self._encoder.add_elemental_features(vec, list(weights.keys()), context, weights=weights)

        if self._encoder.mode in {"configural", "hybrid"} and (compound or self._encoder.mode == "configural"):
            self._encoder.add_compound_feature(vec, features, context)

        return self._apply_salience(vec)

    @property
    def dimension(self) -> int:
        return self._encoder.dimension

