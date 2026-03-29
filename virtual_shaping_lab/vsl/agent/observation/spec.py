"""Typed observation-grammar declaration for V3.19."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any

from .validation import validate_observation_spec


def _to_primitive(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(k): _to_primitive(v) for k, v in sorted(value.items(), key=lambda item: str(item[0]))}
    if isinstance(value, list):
        return [_to_primitive(v) for v in value]
    if isinstance(value, tuple):
        return [_to_primitive(v) for v in value]
    return value


def _require_non_empty_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} must be a non-empty string.")
    return value.strip()


@dataclass(frozen=True)
class ObservationSpec:
    """Declarative observation grammar (representation/context/generalization)."""

    representation: str
    context: str
    generalization: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "representation",
            _require_non_empty_string(self.representation, "ObservationSpec.representation"),
        )
        object.__setattr__(self, "context", _require_non_empty_string(self.context, "ObservationSpec.context"))
        object.__setattr__(
            self,
            "generalization",
            _require_non_empty_string(self.generalization, "ObservationSpec.generalization"),
        )
        if not isinstance(self.metadata, dict):
            raise ValueError("ObservationSpec.metadata must be an object.")
        object.__setattr__(self, "metadata", dict(self.metadata))
        validate_observation_spec(self)

    def to_dict(self) -> dict[str, Any]:
        return {
            "representation": self.representation,
            "context": self.context,
            "generalization": self.generalization,
            "metadata": _to_primitive(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ObservationSpec":
        return cls(
            representation=data.get("representation", ""),
            context=data.get("context", ""),
            generalization=data.get("generalization", ""),
            metadata=data.get("metadata", {}),
        )

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), sort_keys=True, separators=(",", ":"))

    def stable_hash(self) -> str:
        return hashlib.sha256(self.to_json().encode("utf-8")).hexdigest()

