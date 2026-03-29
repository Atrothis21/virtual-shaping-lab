"""Observation-grammar legality validator for V3.19.0."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

REPRESENTATION_VALUES = {"identity", "stimulus_vector", "temporal_basis"}
CONTEXT_VALUES = {"none", "discrete_context", "latent_context"}
GENERALIZATION_VALUES = {"none", "stimulus_similarity", "context_gate"}

REPRESENTATION_TO_GENERALIZATION: dict[str, set[str]] = {
    "identity": {"none"},
    "stimulus_vector": {"none", "stimulus_similarity"},
    "temporal_basis": {"none", "stimulus_similarity", "context_gate"},
}

CONTEXT_TO_GENERALIZATION: dict[str, set[str]] = {
    "none": {"none", "stimulus_similarity"},
    "discrete_context": {"none", "stimulus_similarity", "context_gate"},
    "latent_context": {"none", "context_gate"},
}

GENERALIZATION_REQUIRES_CONTEXT = {
    "context_gate": {"discrete_context", "latent_context"},
}

GENERALIZATION_REQUIRES_REPRESENTATION = {
    "stimulus_similarity": {"stimulus_vector", "temporal_basis"},
    "context_gate": {"temporal_basis"},
}


@dataclass
class ObservationSpecValidationError(ValueError):
    code: str
    message: str

    def __str__(self) -> str:
        return f"[{self.code}] {self.message}"


def _reject(code: str, message: str) -> None:
    raise ObservationSpecValidationError(code=code, message=message)


def validate_observation_spec(spec: Any) -> None:
    """Validate observation tuple legality."""
    representation = getattr(spec, "representation", None)
    context = getattr(spec, "context", None)
    generalization = getattr(spec, "generalization", None)

    if representation not in REPRESENTATION_VALUES:
        _reject("OBS_E_UNKNOWN_REPRESENTATION", f"Unsupported representation '{representation}'.")
    if context not in CONTEXT_VALUES:
        _reject("OBS_E_UNKNOWN_CONTEXT", f"Unsupported context '{context}'.")
    if generalization not in GENERALIZATION_VALUES:
        _reject("OBS_E_UNKNOWN_GENERALIZATION", f"Unsupported generalization '{generalization}'.")

    required_context = GENERALIZATION_REQUIRES_CONTEXT.get(generalization)
    if required_context and context not in required_context:
        allowed = ", ".join(sorted(required_context))
        _reject(
            "OBS_E_GENERALIZATION_REQUIRES_CONTEXT",
            f"Generalization '{generalization}' requires context in {{{allowed}}}.",
        )

    required_representation = GENERALIZATION_REQUIRES_REPRESENTATION.get(generalization)
    if required_representation and representation not in required_representation:
        allowed = ", ".join(sorted(required_representation))
        _reject(
            "OBS_E_GENERALIZATION_REQUIRES_REPRESENTATION",
            f"Generalization '{generalization}' requires representation in {{{allowed}}}.",
        )

    if generalization not in REPRESENTATION_TO_GENERALIZATION[representation]:
        _reject(
            "OBS_E_REPRESENTATION_GENERALIZATION_MISMATCH",
            f"Representation '{representation}' is incompatible with generalization '{generalization}'.",
        )
    if generalization not in CONTEXT_TO_GENERALIZATION[context]:
        _reject(
            "OBS_E_CONTEXT_GENERALIZATION_MISMATCH",
            f"Context '{context}' is incompatible with generalization '{generalization}'.",
        )
