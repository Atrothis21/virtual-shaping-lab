"""Mechanics interfaces for template-driven phases."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

import numpy as np

from experiment.domain.types import PhaseSpec, TrialSchedule, TrialTypeSpec


class ITrialSampler(ABC):
    """Selects a trial type for a given trial index."""

    @abstractmethod
    def reset(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def select_trial_type(
        self,
        *,
        spec: PhaseSpec,
        trial_index: int,
        rng: np.random.Generator,
    ) -> TrialTypeSpec:
        raise NotImplementedError


class ITrialScheduleBuilder(ABC):
    """Builds optional tick-level schedule data for a trial."""

    @abstractmethod
    def build_schedule(
        self,
        *,
        spec: PhaseSpec,
        trial_type: TrialTypeSpec,
        trial_index: int,
    ) -> TrialSchedule | None:
        raise NotImplementedError


class ILearningGate(ABC):
    """Determines whether learning is enabled for a trial."""

    @abstractmethod
    def allows_learning(
        self,
        *,
        spec: PhaseSpec,
        trial_index: int,
    ) -> bool:
        raise NotImplementedError


class IRecordBuilder(ABC):
    """Builds a serializable base trial record."""

    @abstractmethod
    def build_record(
        self,
        *,
        spec: PhaseSpec,
        trial_type: TrialTypeSpec,
        trial_index: int,
        reward: float,
        action: Any,
        context: str,
    ) -> dict[str, Any]:
        raise NotImplementedError
