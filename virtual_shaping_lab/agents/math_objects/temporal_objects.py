"""Concrete temporal basis objects for representation-time encoding."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping

import numpy as np

from virtual_shaping_lab.agents.math_objects.interfaces import ITemporalBasis


@dataclass(frozen=True)
class IdentityTemporalBasis(ITemporalBasis):
    """Identity-style temporal basis.

    Domain/codomain:
    - maps scalar time input to a fixed-dimensional vector carrying direct time features
    - formal shape: `T : Time -> R^d_t`
    """

    dimension: int = 1
    scale: float = 1.0

    def encode(self, t_s: float, dt_s: float | None = None) -> np.ndarray:
        out = np.zeros(self.dimension, dtype=float)
        out[0] = float(t_s) / float(self.scale if self.scale != 0 else 1.0)
        if self.dimension > 1:
            out[1] = float(dt_s or 0.0)
        return out


@dataclass(frozen=True)
class BinnedTemporalBasis(ITemporalBasis):
    """Fixed-bin temporal basis.

    Domain/codomain:
    - maps scalar time input to a one-hot temporal bin vector
    - formal shape: `T : Time -> R^d_t`
    """

    dimension: int
    max_time_s: float = 1.0

    def encode(self, t_s: float, dt_s: float | None = None) -> np.ndarray:
        out = np.zeros(self.dimension, dtype=float)
        max_time = self.max_time_s if self.max_time_s > 0 else 1.0
        clipped = max(0.0, min(float(t_s), max_time))
        ratio = clipped / max_time
        idx = min(self.dimension - 1, int(ratio * self.dimension))
        out[idx] = 1.0
        return out


@dataclass(frozen=True)
class TraceTemporalBasis(ITemporalBasis):
    """Simple exponential trace temporal basis.

    Domain/codomain:
    - maps scalar time input to a fixed bank of exponentially decaying traces
    - formal shape: `T : Time -> R^d_t`
    """

    dimension: int
    decay: float = 1.0

    def encode(self, t_s: float, dt_s: float | None = None) -> np.ndarray:
        base_decay = self.decay if self.decay > 0 else 1.0
        return np.asarray(
            [np.exp(-float(t_s) * base_decay * float(i + 1)) for i in range(self.dimension)],
            dtype=float,
        )


def build_temporal_basis(config: Mapping[str, Any] | None) -> ITemporalBasis | None:
    """Construct a temporal basis from representation params."""
    if not isinstance(config, Mapping):
        return None
    if not bool(config.get("enabled", False)):
        return None

    variant = str(config.get("variant", config.get("name", "identity"))).strip().lower()
    dimension = int(config.get("dimension", 0))
    params = config.get("params", {})
    params = params if isinstance(params, Mapping) else {}

    if variant == "identity":
        return IdentityTemporalBasis(
            dimension=dimension,
            scale=float(params.get("scale", 1.0)),
        )
    if variant == "bins":
        return BinnedTemporalBasis(
            dimension=dimension,
            max_time_s=float(params.get("max_time_s", 1.0)),
        )
    if variant == "traces":
        return TraceTemporalBasis(
            dimension=dimension,
            decay=float(params.get("decay", 1.0)),
        )
    raise ValueError(f"Unknown temporal basis variant '{variant}'")
