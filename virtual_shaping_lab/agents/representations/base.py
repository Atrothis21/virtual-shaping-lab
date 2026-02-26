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

    @abstractmethod
    def encode(self, observation: Observation) -> EncodedState:
        raise NotImplementedError

    @property
    @abstractmethod
    def dimension(self) -> int:
        raise NotImplementedError

    def reset(self) -> None:
        return None

    def get_summary(self) -> Dict[str, Any]:
        return {}
