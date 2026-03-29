"""V3 observation grammar surface."""

from .presets import (
    OBSERVATION_PRESET_ALIASES,
    OBSERVATION_PRESET_FAMILIES,
    OBSERVATION_PRESETS,
    PRESET_VERSION,
    expand_observation_preset,
    observation_preset_aliases,
    observation_preset_families,
    observation_preset_hash,
    observation_preset_names,
    observation_preset_payload,
    observation_preset_registry,
)
from .output import ObservationOutput, normalize_observation_output_dict
from .registry import (
    COMPATIBILITY_MATRIX,
    OBSERVATION_REGISTRY_VERSION,
    SLOT_REGISTRIES,
    compatibility_matrix,
    observation_registry_hash,
    observation_registry_payload,
    slot_registries,
)
from .spec import ObservationSpec
from .validation import ObservationSpecValidationError, validate_observation_spec

__all__ = [
    "ObservationSpec",
    "ObservationSpecValidationError",
    "validate_observation_spec",
    "OBSERVATION_REGISTRY_VERSION",
    "SLOT_REGISTRIES",
    "COMPATIBILITY_MATRIX",
    "slot_registries",
    "compatibility_matrix",
    "observation_registry_payload",
    "observation_registry_hash",
    "PRESET_VERSION",
    "OBSERVATION_PRESETS",
    "OBSERVATION_PRESET_ALIASES",
    "OBSERVATION_PRESET_FAMILIES",
    "observation_preset_names",
    "observation_preset_aliases",
    "observation_preset_registry",
    "observation_preset_families",
    "expand_observation_preset",
    "observation_preset_payload",
    "observation_preset_hash",
    "ObservationOutput",
    "normalize_observation_output_dict",
]
