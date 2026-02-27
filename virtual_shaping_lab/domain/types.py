"""Shared domain data contracts for agent/learner/protocol coordination."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional

import numpy as np


@dataclass(frozen=True)
class Observation:
    """
    Raw environment observation consumed by representations.

    Time fields are optional so time-aware protocols can adopt them incrementally.
    """

    stimuli: list[Any]
    context: Any
    compound: bool = False
    t_s: Optional[float] = None
    dt_s: Optional[float] = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class EncodedState:
    """Vectorized state output by representations and consumed by learners/policies."""

    x: np.ndarray
    key: Optional[str] = None

    def __post_init__(self) -> None:
        vec = np.asarray(self.x, dtype=float)
        if vec.ndim != 1:
            raise ValueError("EncodedState.x must be a 1-D numeric vector.")
        object.__setattr__(self, "x", vec)


@dataclass(frozen=True)
class Transition:
    """
    Standardized transition passed to learners.

    `a` and `s_next` are optional to support Pavlovian and terminal updates.
    """

    s: EncodedState
    r: float
    a: Any = None
    s_next: Optional[EncodedState] = None
    done: bool = False
    t_s: Optional[float] = None
    dt_s: Optional[float] = None
    alpha_override: Optional[float] = None
    delta_override: Optional[float] = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.alpha_override is not None:
            object.__setattr__(self, "alpha_override", float(self.alpha_override))
        if self.delta_override is not None:
            object.__setattr__(self, "delta_override", float(self.delta_override))
