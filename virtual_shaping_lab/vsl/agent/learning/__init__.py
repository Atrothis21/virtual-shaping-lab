"""V3 learner grammar surface."""

from .presets import (
    PRESET_VERSION,
    LEARNER_PRESET_ALIASES,
    LEARNER_PRESET_FAMILIES,
    LEARNER_PRESETS,
    expand_learner_preset,
    learner_preset_aliases,
    learner_preset_families,
    learner_preset_hash,
    learner_preset_names,
    learner_preset_payload,
    learner_preset_registry,
)
from .resolve import resolve_learner_spec
from .adapters import grammar_to_runtime_learner_config, runtime_to_grammar_learner_spec
from .registry import (
    COMPATIBILITY_MATRIX,
    SLOT_REGISTRIES,
    compatibility_matrix,
    learner_registry_hash,
    learner_registry_payload,
    slot_registries,
)
from .spec import LearnerSpec
from .validation import LearnerSpecValidationError, validate_learner_spec

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
    "PRESET_VERSION",
    "LEARNER_PRESETS",
    "LEARNER_PRESET_ALIASES",
    "LEARNER_PRESET_FAMILIES",
    "learner_preset_names",
    "learner_preset_aliases",
    "learner_preset_registry",
    "learner_preset_families",
    "expand_learner_preset",
    "learner_preset_payload",
    "learner_preset_hash",
    "resolve_learner_spec",
    "grammar_to_runtime_learner_config",
    "runtime_to_grammar_learner_spec",
]
