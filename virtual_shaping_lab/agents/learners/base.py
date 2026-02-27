# learners/base.py

"""Base learner definitions for transition-based updates."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Dict, Optional, Any

import numpy as np

from virtual_shaping_lab.agents.interfaces import ILearner
from virtual_shaping_lab.domain.types import EncodedState, Transition


class BaseLearner(ILearner, ABC):
    """Abstract base class for all learning algorithms."""

    learner_type: str = "pavlovian"  # "pavlovian" | "operant" | "both"

    def __init__(self, alpha: float, gamma: float):
        self.alpha = float(alpha)
        self.gamma = float(gamma)
        self.attention_map: Dict[str, float] = {}

    def reset(self) -> None:
        return None

    def set_attention_map(self, attention: Optional[Dict[str, float]]) -> None:
        self.attention_map = dict(attention or {})

    def attention_multiplier(self, cue_labels: Any) -> float:
        if not self.attention_map or cue_labels is None:
            return 1.0
        if isinstance(cue_labels, (str, int, float)):
            return float(self.attention_map.get(str(cue_labels), 1.0))

        labels = [str(c) for c in cue_labels]
        if not labels:
            return 1.0
        vals = [float(self.attention_map.get(lbl, 1.0)) for lbl in labels]
        return sum(vals) / len(vals)

    @abstractmethod
    def update(self, transition: Transition) -> None:
        raise NotImplementedError

    def update_with_alpha(
        self,
        state: EncodedState,
        reward: float,
        action: Any = None,
        alpha_override: Optional[float] = None,
        delta_override: Optional[float] = None,
        next_state: Optional[EncodedState] = None,
        done: bool = False,
        t_s: Optional[float] = None,
        dt_s: Optional[float] = None,
    ) -> None:
        transition = Transition(
            s=state,
            r=reward,
            a=action,
            s_next=next_state,
            done=done,
            t_s=t_s,
            dt_s=dt_s,
            alpha_override=alpha_override,
            delta_override=delta_override,
        )
        self.update(transition)

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
