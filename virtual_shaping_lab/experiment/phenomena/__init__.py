"""Phenomena catalog surface for teaching/preset semantics."""

from experiment.phenomena.catalog import (
    PHENOMENA_REGISTRY,
    PhenomenonSpec,
    available_phenomena,
    get_phenomenon,
    validate_phenomena_registry,
    validate_phenomenon_key,
)

__all__ = [
    "PhenomenonSpec",
    "PHENOMENA_REGISTRY",
    "available_phenomena",
    "validate_phenomenon_key",
    "get_phenomenon",
    "validate_phenomena_registry",
]
