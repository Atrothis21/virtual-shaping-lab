# representations/observation_encoder.py

from typing import Any, Iterable, List
import numpy as np

from agents.representations.vector_encoder import VectorEncoder
from agents.representations.observation import Observation, DEFAULT_CONTEXT


class ObservationVectorEncoder(VectorEncoder):
    """
    Encode an Observation into a vector (multi-hot) with two channels:

      1) Global features:      global:<feature>
      2) Context-gated:        ctx:<context>|<feature>

    Compound feature naming (also gated/global):
      - global:compound:<sorted_features_joined>
      - ctx:<context>|compound:<sorted_features_joined>

    Modes:
      - elemental: A+X -> elemental features only
      - configural: A+X -> compound feature only
      - hybrid: A+X -> elemental + compound
    """

    def __init__(
        self,
        feature_vocab: Iterable[str],
        mode: str = "elemental",
        compound_prefix: str = "compound:",
        context_prefix: str = "ctx:",
        global_prefix: str = "global:",
        include_global: bool = True,
        include_context: bool = True,
    ):
        vocab = list(feature_vocab)
        if not vocab:
            raise ValueError("ObservationVectorEncoder requires a non-empty vocab.")

        if mode not in {"elemental", "configural", "hybrid"}:
            raise ValueError("mode must be one of: elemental, configural, hybrid")

        if not include_global and not include_context:
            raise ValueError("ObservationVectorEncoder requires at least one channel enabled.")

        self._vocab = vocab
        self._index = {f: i for i, f in enumerate(vocab)}
        self._mode = mode
        self._compound_prefix = compound_prefix
        self._context_prefix = context_prefix
        self._global_prefix = global_prefix
        self._include_global = include_global
        self._include_context = include_context

    def _compound_key(self, features: List[Any]) -> str:
        parts = [str(f) for f in sorted(features)]
        return f"{self._compound_prefix}{'|'.join(parts)}"

    def _ctx_key(self, context: Any, feature: str) -> str:
        return f"{self._context_prefix}{context}|{feature}"

    def _global_key(self, feature: str) -> str:
        return f"{self._global_prefix}{feature}"

    def _add_feature(self, vec: np.ndarray, key: str, value: float = 1.0) -> None:
        if key not in self._index:
            raise ValueError(f"Unknown feature: '{key}'")
        vec[self._index[key]] += value

    def add_elemental_features(
        self,
        vec: np.ndarray,
        features: List[Any],
        context: Any,
        weights: dict | None = None,
    ) -> None:
        for f in features:
            weight = 1.0
            if weights is not None:
                weight = float(weights.get(str(f), 1.0))
            if self._include_global:
                self._add_feature(vec, self._global_key(str(f)), weight)
            if self._include_context:
                self._add_feature(vec, self._ctx_key(context, str(f)), weight)

    def add_compound_feature(self, vec: np.ndarray, features: List[Any], context: Any) -> None:
        c_key = self._compound_key(features)
        if self._include_global:
            self._add_feature(vec, self._global_key(c_key), 1.0)
        if self._include_context:
            self._add_feature(vec, self._ctx_key(context, c_key), 1.0)

    def encode(self, observation: Observation) -> np.ndarray:
        features = observation.get("stimuli", [])
        compound = observation.get("compound", False)
        context = observation.get("context", DEFAULT_CONTEXT)

        vec = np.zeros(self.dimension, dtype=float)

        # Elemental features
        if self._mode in {"elemental", "hybrid"}:
            self.add_elemental_features(vec, features, context, weights=None)

        # Compound feature
        if self._mode in {"configural", "hybrid"} and (compound or self._mode == "configural"):
            self.add_compound_feature(vec, features, context)
        return vec

    @property
    def mode(self) -> str:
        return self._mode

    @property
    def dimension(self) -> int:
        return len(self._vocab)

