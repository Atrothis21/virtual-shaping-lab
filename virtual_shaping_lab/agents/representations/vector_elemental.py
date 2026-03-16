# representations/vector_elemental.py

from __future__ import annotations

from typing import Any, Dict, Optional

import numpy as np

from virtual_shaping_lab.agents.math_objects.representation_objects import DefaultContextMap, MatrixSimilarityKernel
from virtual_shaping_lab.agents.math_objects.salience_objects import DiagonalSalienceOperator
from virtual_shaping_lab.agents.math_objects.temporal_objects import build_temporal_basis
from virtual_shaping_lab.agents.representations.base import RepresentationBase
from virtual_shaping_lab.agents.representations.mechanisms import encode_with_mechanisms
from virtual_shaping_lab.agents.representations.observation_encoder import ObservationVectorEncoder
from virtual_shaping_lab.agents.representations.vocab import build_feature_vocab
from virtual_shaping_lab.agents.representations.similarity import parse_similarity_matrix
from virtual_shaping_lab.domain.types import EncodedState, Observation


class VectorElementalRepresentation(RepresentationBase):
    name = "vector_elemental"

    def __init__(self, params: Optional[Dict[str, Any]] = None):
        super().__init__(params=params)
        stimuli = self.params.get("stimuli")
        if not stimuli:
            raise ValueError("vector_elemental requires params['stimuli']")

        salience = self.params.get("salience", {})
        similarity = self.params.get("similarity")
        compound_prefix = self.params.get("compound_prefix", "compound:")
        max_compound_size = self.params.get("max_compound_size", 2)
        contexts = self.params.get("contexts")
        context_prefix = self.params.get("context_prefix", "ctx:")
        global_prefix = self.params.get("global_prefix", "global:")
        include_global = self.params.get("include_global", True)
        include_context = self.params.get("include_context", True)

        features, salience_vector = build_feature_vocab(
            stimuli=stimuli,
            include_compounds=False,
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
            mode="elemental",
            compound_prefix=compound_prefix,
            context_prefix=context_prefix,
            global_prefix=global_prefix,
            include_global=include_global,
            include_context=include_context,
        )

        self.salience = np.asarray(salience_vector, dtype=float)
        self.similarity_map = parse_similarity_matrix(similarity, stimuli) if similarity else {}
        self.context_map = self.params.get("context_map") or DefaultContextMap()
        self.similarity_kernel = self.params.get("similarity_kernel") or MatrixSimilarityKernel(self.similarity_map)
        self.salience_operator = self.params.get("salience_operator") or DiagonalSalienceOperator(self.salience)
        self.temporal_basis = self.params.get("temporal_basis_object") or build_temporal_basis(self.params.get("temporal_basis"))

    def encode(self, observation: Observation) -> EncodedState:
        vec = encode_with_mechanisms(
            self._encoder,
            observation,
            similarity_map=self.similarity_map,
            salience=self.salience,
            context_map=self.context_map,
            similarity_kernel=self.similarity_kernel,
            salience_operator=self.salience_operator,
        )
        if self.temporal_basis is not None:
            t_s = 0.0 if observation.t_s is None else float(observation.t_s)
            dt_s = None if observation.dt_s is None else float(observation.dt_s)
            vec = np.concatenate([vec, self.temporal_basis.encode(t_s=t_s, dt_s=dt_s)])
        return EncodedState(x=vec)

    @property
    def dimension(self) -> int:
        temporal_dim = self.temporal_basis.dimension if self.temporal_basis is not None else 0
        return self._encoder.dimension + temporal_dim

