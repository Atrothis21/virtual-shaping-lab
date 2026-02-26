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
    t_s: Optional[float] = None
    dt_s: Optional[float] = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class EncodedState:
    """
    Vectorized state output by representations and consumed by learners/policies.
    """

    x: np.ndarray
    key: Optional[str] = None


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
    metadata: dict[str, Any] = field(default_factory=dict)
