"""Compatibility adapters from legacy phase/protocol runtime units to IRunnableUnit."""

from __future__ import annotations

from typing import Any, Iterator

from experiment.runner import Runner
from virtual_shaping_lab.domain.types import Observation
from virtual_shaping_lab.experiment.domain.interfaces import IPhase, IProtocol
from virtual_shaping_lab.experiment.domain.types import ExperimentContext, StepResult


def _record_to_step(record: dict[str, Any], *, done: bool) -> StepResult:
    context = record.get("context", "A")
    obs = Observation(stimuli=[], context=context, metadata={"record": record})
    reward = float(record.get("reward", 0.0))
    return StepResult(
        observation=obs,
        available_actions=[],
        reward=reward,
        learning_enabled=True,
        done=done,
        metadata={"record": record},
    )


class PhaseUnitAdapter(IPhase):
    """IRunnableUnit adapter for legacy PhaseBase units."""

    def __init__(self, phase: Any):
        self.phase = phase

    def reset(self, ctx: ExperimentContext) -> None:
        if hasattr(self.phase, "reset"):
            self.phase.reset()
            return
        if hasattr(self.phase, "trial_index"):
            self.phase.trial_index = 0
        if hasattr(self.phase, "records"):
            self.phase.records = []

    def iter_steps(self, ctx: ExperimentContext) -> Iterator[StepResult]:
        records = Runner(self.phase, context=ctx).run()
        total = len(records)
        for i, rec in enumerate(records):
            yield _record_to_step(rec, done=(i == total - 1))


class ProtocolUnitAdapter(IProtocol):
    """IRunnableUnit adapter for legacy BaseProtocol-like units."""

    def __init__(self, protocol: Any):
        self.protocol = protocol

    def reset(self, ctx: ExperimentContext) -> None:
        if hasattr(self.protocol, "reset"):
            self.protocol.reset()
            return
        if hasattr(self.protocol, "trial_index"):
            self.protocol.trial_index = 0
        if hasattr(self.protocol, "records"):
            self.protocol.records = []

    def iter_steps(self, ctx: ExperimentContext) -> Iterator[StepResult]:
        records = Runner(self.protocol, context=ctx).run()
        total = len(records)
        for i, rec in enumerate(records):
            yield _record_to_step(rec, done=(i == total - 1))
