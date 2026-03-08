# learners/base.py

"""Base learner definitions for transition-based updates."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Dict, Optional, Any, Mapping

import numpy as np

from virtual_shaping_lab.agents.interfaces import ILearner
from virtual_shaping_lab.agents.learners.attention_strategies import (
    AttentionContext,
    AttentionStrategy,
    build_attention_strategy,
)
from virtual_shaping_lab.domain.types import EncodedState, META_CUE_LABELS, Transition


class BaseLearner(ILearner, ABC):
    """Abstract base class for all learning algorithms."""

    learner_type: str = "pavlovian"  # "pavlovian" | "operant" | "both"

    def __init__(self, alpha: float, gamma: float):
        self.alpha = float(alpha)
        self.gamma = float(gamma)
        self.attention_map: Dict[str, float] = {}
        self._attention_strategy: AttentionStrategy = build_attention_strategy("none")

    def reset(self) -> None:
        self._attention_strategy.reset()
        return None

    def set_attention_map(self, attention: Optional[Dict[str, float]]) -> None:
        self.attention_map = dict(attention or {})
        self.set_attention_config(
            name="static" if self.attention_map else "none",
            params={
                "default": 1.0,
                "overrides": dict(self.attention_map),
            },
        )

    def set_attention_config(self, *, name: str, params: Optional[Mapping[str, Any]] = None) -> None:
        self._attention_strategy = build_attention_strategy(name=name, params=params)

    def attention_multiplier(self, cue_labels: Any) -> float:
        return float(self._attention_strategy.current_alpha_for_cues(cue_labels))

    def update_attention_state(self, context: AttentionContext) -> None:
        self._attention_strategy.update_state(context)

    @abstractmethod
    def update(self, transition: Transition) -> None:
        raise NotImplementedError

    def effective_alpha(self, transition: Transition) -> float:
        cue_labels = transition.metadata.get(META_CUE_LABELS)
        return float(self.alpha) * float(self.attention_multiplier(cue_labels))

    @abstractmethod
    def value(self, state: EncodedState, action: Any = None) -> float:
        raise NotImplementedError

    def expects_action(self) -> bool:
        return False

    def start_episode(self) -> None:
        return None

    def end_episode(self) -> None:
        return None

    def get_parameters(self) -> Dict[str, np.ndarray]:
        return {}
