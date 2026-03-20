"""Typed phenomenon-registry contracts for V3 scientific coverage."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any

SUPPORTED_CAVEAT_TIERS: tuple[str, ...] = (
    "none",
    "minor",
    "moderate",
    "major",
)


def _to_primitive(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(k): _to_primitive(v) for k, v in sorted(value.items(), key=lambda item: str(item[0]))}
    if isinstance(value, list):
        return [_to_primitive(v) for v in value]
    if isinstance(value, tuple):
        return [_to_primitive(v) for v in value]
    if hasattr(value, "to_dict"):
        return _to_primitive(value.to_dict())
    return value


@dataclass(frozen=True)
class OperatorBundleSpec:
    """Minimal operator bundle declaration for a phenomenon entry."""

    key: str
    operators: tuple[str, ...]
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.key, str) or not self.key.strip():
            raise ValueError("OperatorBundleSpec.key must be a non-empty string.")
        if not isinstance(self.operators, tuple) or not self.operators:
            raise ValueError("OperatorBundleSpec.operators must be a non-empty tuple[str, ...].")
        if not all(isinstance(value, str) and value.strip() for value in self.operators):
            raise ValueError("OperatorBundleSpec.operators must contain non-empty strings.")
        if not isinstance(self.metadata, dict):
            raise ValueError("OperatorBundleSpec.metadata must be an object.")

    def to_dict(self) -> dict[str, Any]:
        return {
            "key": self.key,
            "operators": list(self.operators),
            "metadata": _to_primitive(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "OperatorBundleSpec":
        return cls(
            key=str(data.get("key", "")).strip(),
            operators=tuple(str(v).strip() for v in (data.get("operators", ()) or ())),
            metadata=dict(data.get("metadata", {}) or {}),
        )


@dataclass(frozen=True)
class ConstraintSpec:
    """Constraint contract used to enforce operator requirements."""

    required_operators: tuple[str, ...] = ()
    forbidden_operators: tuple[str, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.required_operators, tuple):
            raise ValueError("ConstraintSpec.required_operators must be tuple[str, ...].")
        if not isinstance(self.forbidden_operators, tuple):
            raise ValueError("ConstraintSpec.forbidden_operators must be tuple[str, ...].")
        if not all(isinstance(value, str) and value.strip() for value in self.required_operators):
            raise ValueError("ConstraintSpec.required_operators must contain non-empty strings.")
        if not all(isinstance(value, str) and value.strip() for value in self.forbidden_operators):
            raise ValueError("ConstraintSpec.forbidden_operators must contain non-empty strings.")
        overlap = set(self.required_operators).intersection(self.forbidden_operators)
        if overlap:
            names = ", ".join(sorted(overlap))
            raise ValueError(f"ConstraintSpec overlap is not allowed; found in required/forbidden: {names}.")
        if not isinstance(self.metadata, dict):
            raise ValueError("ConstraintSpec.metadata must be an object.")

    def to_dict(self) -> dict[str, Any]:
        return {
            "required_operators": list(self.required_operators),
            "forbidden_operators": list(self.forbidden_operators),
            "metadata": _to_primitive(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ConstraintSpec":
        return cls(
            required_operators=tuple(str(v).strip() for v in (data.get("required_operators", ()) or ())),
            forbidden_operators=tuple(str(v).strip() for v in (data.get("forbidden_operators", ()) or ())),
            metadata=dict(data.get("metadata", {}) or {}),
        )


@dataclass(frozen=True)
class ReadoutSpec:
    """Named readout contract for a phenomenon entry."""

    key: str
    metric: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.key, str) or not self.key.strip():
            raise ValueError("ReadoutSpec.key must be a non-empty string.")
        if not isinstance(self.metric, str) or not self.metric.strip():
            raise ValueError("ReadoutSpec.metric must be a non-empty string.")
        if not isinstance(self.metadata, dict):
            raise ValueError("ReadoutSpec.metadata must be an object.")

    def to_dict(self) -> dict[str, Any]:
        return {
            "key": self.key,
            "metric": self.metric,
            "metadata": _to_primitive(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ReadoutSpec":
        return cls(
            key=str(data.get("key", "")).strip(),
            metric=str(data.get("metric", "")).strip(),
            metadata=dict(data.get("metadata", {}) or {}),
        )


@dataclass(frozen=True)
class PhenomenonRegistryEntry:
    """Schema contract for a single phenomenon registry entry."""

    key: str
    recipe: dict[str, Any]
    bundles: tuple[OperatorBundleSpec, ...]
    constraints: ConstraintSpec
    readouts: tuple[ReadoutSpec, ...]
    fixture: str
    caveat_tier: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.key, str) or not self.key.strip():
            raise ValueError("PhenomenonRegistryEntry.key must be a non-empty string.")
        if not isinstance(self.recipe, dict):
            raise ValueError("PhenomenonRegistryEntry.recipe must be an object.")
        if not isinstance(self.bundles, tuple) or not self.bundles:
            raise ValueError("PhenomenonRegistryEntry.bundles must be a non-empty tuple[OperatorBundleSpec, ...].")
        if not all(isinstance(value, OperatorBundleSpec) for value in self.bundles):
            raise ValueError("PhenomenonRegistryEntry.bundles must contain OperatorBundleSpec values.")
        if not isinstance(self.constraints, ConstraintSpec):
            raise ValueError("PhenomenonRegistryEntry.constraints must be a ConstraintSpec.")
        if not isinstance(self.readouts, tuple) or not self.readouts:
            raise ValueError("PhenomenonRegistryEntry.readouts must be a non-empty tuple[ReadoutSpec, ...].")
        if not all(isinstance(value, ReadoutSpec) for value in self.readouts):
            raise ValueError("PhenomenonRegistryEntry.readouts must contain ReadoutSpec values.")
        if not isinstance(self.fixture, str) or not self.fixture.strip():
            raise ValueError("PhenomenonRegistryEntry.fixture must be a non-empty string.")
        if not isinstance(self.caveat_tier, str) or not self.caveat_tier.strip():
            raise ValueError("PhenomenonRegistryEntry.caveat_tier must be a non-empty string.")
        if self.caveat_tier not in SUPPORTED_CAVEAT_TIERS:
            allowed = ", ".join(SUPPORTED_CAVEAT_TIERS)
            raise ValueError(
                f"PhenomenonRegistryEntry.caveat_tier must be one of: {allowed}."
            )
        if not isinstance(self.metadata, dict):
            raise ValueError("PhenomenonRegistryEntry.metadata must be an object.")

    def to_dict(self) -> dict[str, Any]:
        return {
            "key": self.key,
            "recipe": _to_primitive(self.recipe),
            "bundles": [_to_primitive(bundle) for bundle in self.bundles],
            "constraints": _to_primitive(self.constraints),
            "readouts": [_to_primitive(readout) for readout in self.readouts],
            "fixture": self.fixture,
            "caveat_tier": self.caveat_tier,
            "metadata": _to_primitive(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "PhenomenonRegistryEntry":
        raw_bundles = list(data.get("bundles", ()) or ())
        raw_readouts = list(data.get("readouts", ()) or ())
        raw_constraints = data.get("constraints", {}) or {}
        return cls(
            key=str(data.get("key", "")).strip(),
            recipe=dict(data.get("recipe", {}) or {}),
            bundles=tuple(
                OperatorBundleSpec.from_dict(item) if isinstance(item, dict) else item for item in raw_bundles
            ),
            constraints=ConstraintSpec.from_dict(raw_constraints) if isinstance(raw_constraints, dict) else raw_constraints,
            readouts=tuple(ReadoutSpec.from_dict(item) if isinstance(item, dict) else item for item in raw_readouts),
            fixture=str(data.get("fixture", "")).strip(),
            caveat_tier=str(data.get("caveat_tier", "")).strip(),
            metadata=dict(data.get("metadata", {}) or {}),
        )


PHENOMENON_REGISTRY: dict[str, PhenomenonRegistryEntry] = {}


def validate_phenomenon_registry(
    registry: dict[str, PhenomenonRegistryEntry] | None = None,
) -> None:
    active = registry if registry is not None else PHENOMENON_REGISTRY
    for key, value in active.items():
        if not isinstance(value, PhenomenonRegistryEntry):
            raise ValueError(f"Phenomenon registry value for '{key}' must be PhenomenonRegistryEntry.")
        if key != value.key:
            raise ValueError(f"Phenomenon registry key mismatch: '{key}' != '{value.key}'.")


def phenomenon_registry_payload(
    registry: dict[str, PhenomenonRegistryEntry] | None = None,
) -> dict[str, Any]:
    active = registry if registry is not None else PHENOMENON_REGISTRY
    validate_phenomenon_registry(active)
    return {
        "entries": {key: active[key].to_dict() for key in sorted(active.keys())},
        "supported_caveat_tiers": list(SUPPORTED_CAVEAT_TIERS),
        "version": "3.8.0",
    }


def phenomenon_registry_hash(
    registry: dict[str, PhenomenonRegistryEntry] | None = None,
) -> str:
    payload = phenomenon_registry_payload(registry)
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()

