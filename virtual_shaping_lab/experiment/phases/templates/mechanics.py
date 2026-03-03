"""Concrete mechanics implementations for PhaseTemplate."""

from __future__ import annotations

from typing import Any

import numpy as np

from experiment.domain.types import (
    OperantContingencySpec,
    PhaseSpec,
    TrialSchedule,
    TrialTypeSpec,
)
from experiment.phases.templates.interfaces import (
    ILearningGate,
    IRecordBuilder,
    ITrialSampler,
    ITrialScheduleBuilder,
)


class WeightedRandomSampler(ITrialSampler):
    """Sample trial types according to `TrialTypeSpec.weight`."""

    def reset(self) -> None:
        return None

    def select_trial_type(
        self,
        *,
        spec: PhaseSpec,
        trial_index: int,
        rng: np.random.Generator,
    ) -> TrialTypeSpec:
        weights = np.asarray([float(tt.weight) for tt in spec.trial_types], dtype=float)
        weights = np.clip(weights, 0.0, None)
        if float(weights.sum()) <= 0.0:
            weights = np.ones(len(spec.trial_types), dtype=float)
        probs = weights / weights.sum()
        idx = int(rng.choice(len(spec.trial_types), p=probs))
        return spec.trial_types[idx]


class BlockedSampler(ITrialSampler):
    """Cycle through trial types in a deterministic balanced block."""

    def reset(self) -> None:
        return None

    def select_trial_type(
        self,
        *,
        spec: PhaseSpec,
        trial_index: int,
        rng: np.random.Generator,
    ) -> TrialTypeSpec:
        idx = int(trial_index % len(spec.trial_types))
        return spec.trial_types[idx]


class FixedSequenceSampler(ITrialSampler):
    """Follow an explicit trial-type label sequence."""

    def __init__(self, sequence: list[str]):
        self.sequence = list(sequence)

    def reset(self) -> None:
        return None

    def select_trial_type(
        self,
        *,
        spec: PhaseSpec,
        trial_index: int,
        rng: np.random.Generator,
    ) -> TrialTypeSpec:
        if not self.sequence:
            return spec.trial_types[trial_index % len(spec.trial_types)]
        label = self.sequence[trial_index % len(self.sequence)]
        for tt in spec.trial_types:
            if tt.label == label:
                return tt
        return spec.trial_types[trial_index % len(spec.trial_types)]


class PavlovianScheduleBuilder(ITrialScheduleBuilder):
    """Build trial schedule with no action set."""

    def build_schedule(
        self,
        *,
        spec: PhaseSpec,
        trial_type: TrialTypeSpec,
        trial_index: int,
    ) -> TrialSchedule | None:
        return TrialSchedule(
            time=spec.time,
            base_stimuli=list(trial_type.stimuli),
            available_actions=[],
            metadata={},
        )


class OperantScheduleBuilder(ITrialScheduleBuilder):
    """Build trial schedule with operant actions and schedule runtime metadata."""

    def build_schedule(
        self,
        *,
        spec: PhaseSpec,
        trial_type: TrialTypeSpec,
        trial_index: int,
    ) -> TrialSchedule | None:
        actions: list[Any] = []
        metadata: dict[str, Any] = {}
        if isinstance(spec.contingency, OperantContingencySpec):
            actions = list(spec.contingency.action_labels)
            if isinstance(spec.contingency.schedule_runtime, dict):
                # Reuses the existing runtime metadata contract consumed by TrialExecutor.
                metadata["schedule_runtime"] = dict(spec.contingency.schedule_runtime)
        return TrialSchedule(
            time=spec.time,
            base_stimuli=list(trial_type.stimuli),
            available_actions=actions,
            metadata=metadata,
        )


class AlwaysLearn(ILearningGate):
    def allows_learning(self, *, spec: PhaseSpec, trial_index: int) -> bool:
        return True


class NeverLearn(ILearningGate):
    def allows_learning(self, *, spec: PhaseSpec, trial_index: int) -> bool:
        return False


class SpecLearningGate(ILearningGate):
    """Default gate that follows `spec.learning.enabled`."""

    def allows_learning(self, *, spec: PhaseSpec, trial_index: int) -> bool:
        return bool(spec.learning.enabled)


class DefaultRecordBuilder(IRecordBuilder):
    """Default serializable base record for template phases."""

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
        stimulus = (
            trial_type.stimuli[0]
            if len(trial_type.stimuli) == 1
            else tuple(trial_type.stimuli)
        )
        return {
            "phase": spec.key,
            "phase_name": spec.name,
            "trial": trial_index,
            "trial_type": trial_type.label,
            "stimulus": stimulus,
            "context": context,
            "action": action,
            "reward": float(reward),
            "learning_enabled": bool(spec.learning.enabled),
        }
