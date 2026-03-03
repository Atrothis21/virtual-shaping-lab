"""Template-driven phase composites and mechanics interfaces."""

from experiment.phases.templates.interfaces import (
    ILearningGate,
    IRecordBuilder,
    ITrialSampler,
    ITrialScheduleBuilder,
)
from experiment.phases.templates.mechanics import (
    AlwaysLearn,
    BlockedSampler,
    DefaultRecordBuilder,
    FixedSequenceSampler,
    NeverLearn,
    OperantScheduleBuilder,
    PavlovianScheduleBuilder,
    SpecLearningGate,
    WeightedRandomSampler,
)
from experiment.phases.templates.phase_template import PhaseTemplate

__all__ = [
    "ILearningGate",
    "IRecordBuilder",
    "ITrialSampler",
    "ITrialScheduleBuilder",
    "AlwaysLearn",
    "BlockedSampler",
    "DefaultRecordBuilder",
    "FixedSequenceSampler",
    "NeverLearn",
    "OperantScheduleBuilder",
    "PavlovianScheduleBuilder",
    "SpecLearningGate",
    "WeightedRandomSampler",
    "PhaseTemplate",
]
