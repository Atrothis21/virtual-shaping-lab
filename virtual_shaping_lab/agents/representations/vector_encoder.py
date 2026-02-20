# representations/vector_encoder.py

from abc import ABC, abstractmethod
from typing import Any, Dict, Iterable, List
import numpy as np


class VectorEncoder(ABC):
    """
    Base contract for encoders that return vectors.

    Vector-first contract:
        - encode() returns a 1-D numpy vector
        - dimension is a fixed integer
    """

    @abstractmethod
    def encode(self, observation: Any) -> np.ndarray:
        """
        Convert an observation into a 1-D state vector.
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def dimension(self) -> int:
        """
        Dimensionality of the encoded state vector.
        """
        raise NotImplementedError


class IdentityVectorEncoder(VectorEncoder):
    """
    Pass-through encoder for environments that already emit vectors.
    """

    def __init__(self, dimension: int):
        self._dimension = dimension

    def encode(self, observation: np.ndarray) -> np.ndarray:
        vec = np.asarray(observation, dtype=float)
        if vec.ndim != 1 or vec.size != self._dimension:
            raise ValueError(
                f"Expected observation of shape ({self._dimension},)"
            )
        return vec

    @property
    def dimension(self) -> int:
        return self._dimension


class FeatureListVectorEncoder(VectorEncoder):
    """
    Encode a list of feature labels into a multi-hot vector.

    Accepts:
        - list[str] (e.g., ["A", "B"])
        - single str (e.g., "A")
    """

    def __init__(self, feature_vocab: Iterable[str]):
        vocab = list(feature_vocab)
        if not vocab:
            raise ValueError("FeatureListVectorEncoder requires a non-empty vocab.")

        self._vocab: List[str] = vocab
        self._index: Dict[str, int] = {f: i for i, f in enumerate(vocab)}

    def encode(self, observation: Any) -> np.ndarray:
        if isinstance(observation, str):
            features = [observation]
        elif isinstance(observation, list):
            features = observation
        else:
            raise ValueError(
                "FeatureListVectorEncoder expects a str or list[str] observation."
            )

        vec = np.zeros(self.dimension, dtype=float)
        for f in features:
            if f not in self._index:
                raise ValueError(f"Unknown feature label: '{f}'")
            vec[self._index[f]] = 1.0

        return vec

    @property
    def dimension(self) -> int:
        return len(self._vocab)
