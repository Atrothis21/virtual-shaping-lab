"""Typed observation output contract and legacy-name normalization."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

_LEGACY_KEY_ALIASES: dict[str, str] = {
    "raw_observation": "raw_stimulus",
    "state_representation": "representation",
    "context": "context_state",
    "generalized": "generalized_state",
    "feature_vector": "features",
    "feature_labels": "feature_names",
}

_REQUIRED_KEYS: tuple[str, ...] = (
    "raw_stimulus",
    "representation",
    "context_state",
    "generalized_state",
    "features",
    "feature_names",
    "metadata",
)


def _normalize_payload(data: dict[str, Any]) -> dict[str, Any]:
    normalized: dict[str, Any] = {}
    for key, value in data.items():
        canonical = _LEGACY_KEY_ALIASES.get(str(key), str(key))
        normalized[canonical] = value
    normalized.setdefault("metadata", {})
    return normalized


def normalize_observation_output_dict(data: dict[str, Any]) -> dict[str, Any]:
    """Normalize payload keys to canonical observation-output names."""
    if not isinstance(data, dict):
        raise ValueError("ObservationOutput payload must be an object.")
    normalized = _normalize_payload(data)
    return {
        "raw_stimulus": normalized.get("raw_stimulus"),
        "representation": normalized.get("representation"),
        "context_state": normalized.get("context_state"),
        "generalized_state": normalized.get("generalized_state"),
        "features": normalized.get("features"),
        "feature_names": normalized.get("feature_names"),
        "metadata": normalized.get("metadata"),
    }


@dataclass(frozen=True)
class ObservationOutput:
    """Typed observation artifact emitted by observation materialization."""

    raw_stimulus: Any
    representation: Any
    context_state: Any
    generalized_state: Any
    features: list[float] = field(default_factory=list)
    feature_names: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.features, list):
            raise ValueError("ObservationOutput.features must be a list.")
        if not all(isinstance(value, (int, float)) for value in self.features):
            raise ValueError("ObservationOutput.features must contain numeric values.")
        if not isinstance(self.feature_names, list):
            raise ValueError("ObservationOutput.feature_names must be a list.")
        if not all(isinstance(value, str) for value in self.feature_names):
            raise ValueError("ObservationOutput.feature_names must contain strings.")
        if not isinstance(self.metadata, dict):
            raise ValueError("ObservationOutput.metadata must be an object.")
        if len(self.feature_names) not in {0, len(self.features)}:
            raise ValueError("ObservationOutput.feature_names must be empty or match features length.")
        object.__setattr__(self, "features", [float(value) for value in self.features])
        object.__setattr__(self, "feature_names", [str(value) for value in self.feature_names])
        object.__setattr__(self, "metadata", dict(self.metadata))

    def to_dict(self) -> dict[str, Any]:
        return {
            "raw_stimulus": self.raw_stimulus,
            "representation": self.representation,
            "context_state": self.context_state,
            "generalized_state": self.generalized_state,
            "features": list(self.features),
            "feature_names": list(self.feature_names),
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ObservationOutput":
        normalized = normalize_observation_output_dict(data)
        missing = [key for key in _REQUIRED_KEYS if key not in normalized]
        if missing:
            joined = ", ".join(sorted(missing))
            raise ValueError(f"ObservationOutput payload missing keys: {joined}")
        return cls(
            raw_stimulus=normalized["raw_stimulus"],
            representation=normalized["representation"],
            context_state=normalized["context_state"],
            generalized_state=normalized["generalized_state"],
            features=normalized["features"] if normalized["features"] is not None else [],
            feature_names=normalized["feature_names"] if normalized["feature_names"] is not None else [],
            metadata=normalized["metadata"] if normalized["metadata"] is not None else {},
        )

