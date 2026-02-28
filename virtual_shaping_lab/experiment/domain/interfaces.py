"""Experiment-layer interfaces for v2.1 orchestration."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Iterator

from virtual_shaping_lab.experiment.domain.types import (
    ExperimentContext,
    RunResult,
    StepResult,
    TrialRecord,
)


class IRecordSink(ABC):
    """Destination for emitted trial records."""

    @abstractmethod
    def emit(self, record: TrialRecord) -> None:
        raise NotImplementedError

    @abstractmethod
    def close(self) -> None:
        raise NotImplementedError


class IRunnableUnit(ABC):
    """Common execution contract for phases and protocols."""

    @abstractmethod
    def reset(self, ctx: ExperimentContext) -> None:
        raise NotImplementedError

    @abstractmethod
    def iter_steps(self, ctx: ExperimentContext) -> Iterator[StepResult]:
        raise NotImplementedError


class IPhase(IRunnableUnit, ABC):
    """Marker contract for phase units."""


class IProtocol(IRunnableUnit, ABC):
    """Marker contract for protocol units."""


class IRunner(ABC):
    """Generic runtime executor."""

    @abstractmethod
    def run(self, ctx: ExperimentContext, unit: IRunnableUnit, sink: IRecordSink) -> RunResult:
        raise NotImplementedError

