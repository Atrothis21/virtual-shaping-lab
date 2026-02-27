# representations/base.py

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from virtual_shaping_lab.agents.interfaces import IRepresentation
from virtual_shaping_lab.domain.types import EncodedState, Observation


class RepresentationBase(IRepresentation, ABC):
    """Base class for all vector-first representations."""

    name: str = "base"

    def __init__(self, params: Optional[Dict[str, Any]] = None):
        self.params = params or {}
        self._validate_mechanism_ownership()

    def _validate_mechanism_ownership(self) -> None:
        forbidden = []
        if "attention" in self.params:
            forbidden.append("attention")
        if "attention_compound" in self.params:
            forbidden.append("attention_compound")
        if forbidden:
            names = ", ".join(forbidden)
            raise ValueError(
                f"Representation params must not define {names}; attention is learner-owned in v2."
            )

    @abstractmethod
    def encode(self, observation: Observation) -> EncodedState:
        raise NotImplementedError

    @property
    @abstractmethod
    def dimension(self) -> int:
        raise NotImplementedError

    def reset(self) -> None:
        return None

    def timing_fields(self, observation: Observation) -> Dict[str, Any]:
        """Return normalized timing fields for time-aware encoders."""
        return {
            "t_s": observation.t_s,
            "dt_s": observation.dt_s,
            "trial_step": observation.trial_step,
            "trial_id": observation.trial_id,
        }

    def get_summary(self) -> Dict[str, Any]:
        return {}
