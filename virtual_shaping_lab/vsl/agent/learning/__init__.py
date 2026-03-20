"""V3 learner grammar surface."""

from .registry import (
    COMPATIBILITY_MATRIX,
    SLOT_REGISTRIES,
    compatibility_matrix,
    learner_registry_hash,
    learner_registry_payload,
    slot_registries,
)
from .spec import LearnerSpec
from .validator import LearnerSpecValidationError, validate_learner_spec

__all__ = [
    "LearnerSpec",
    "LearnerSpecValidationError",
    "validate_learner_spec",
    "SLOT_REGISTRIES",
    "COMPATIBILITY_MATRIX",
    "slot_registries",
    "compatibility_matrix",
    "learner_registry_payload",
    "learner_registry_hash",
]
