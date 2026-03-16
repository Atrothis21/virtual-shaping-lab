"""Concrete attention mechanism objects backed by learner attention strategies."""

from __future__ import annotations

from typing import Any, Mapping

from virtual_shaping_lab.agents.learners.attention_strategies import (
    AttentionContext,
    AttentionState,
    BaseAttentionStrategy,
    MackintoshAttentionStrategy,
    NoAttentionStrategy,
    PearceHallAttentionStrategy,
    StaticAttentionStrategy,
    build_attention_strategy,
)
from virtual_shaping_lab.agents.math_objects.interfaces import IAttentionMechanism


AttentionMechanism = IAttentionMechanism


def build_attention_mechanism(name: str, *, params: Mapping[str, Any] | None = None) -> AttentionMechanism:
    """Build an attention mechanism object using the existing strategy implementations."""
    return build_attention_strategy(name=name, params=params)


__all__ = [
    "AttentionContext",
    "AttentionState",
    "AttentionMechanism",
    "BaseAttentionStrategy",
    "NoAttentionStrategy",
    "StaticAttentionStrategy",
    "PearceHallAttentionStrategy",
    "MackintoshAttentionStrategy",
    "build_attention_mechanism",
]
