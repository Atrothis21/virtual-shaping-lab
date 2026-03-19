"""Typed operator-pipeline declarations for V3 runtime sequencing."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any

NORMATIVE_STAGE_ORDER: tuple[str, ...] = (
    "Phi",
    "C",
    "G",
    "E",
    "P",
    "Policy",
    "Env",
    "Err",
    "A",
    "Update",
    "Measure",
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
class OperatorStage:
    """Declarative stage identity inside an operator pipeline."""

    key: str
    name: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.key, str) or not self.key.strip():
            raise ValueError("OperatorStage.key must be a non-empty string.")
        if self.name is not None and (not isinstance(self.name, str) or not self.name.strip()):
            raise ValueError("OperatorStage.name must be a non-empty string when provided.")
        if not isinstance(self.metadata, dict):
            raise ValueError("OperatorStage.metadata must be an object.")
        if self.name is None:
            object.__setattr__(self, "name", self.key)

    def to_dict(self) -> dict[str, Any]:
        return {
            "key": self.key,
            "name": self.name,
            "metadata": _to_primitive(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "OperatorStage":
        return cls(
            key=str(data.get("key", "")).strip(),
            name=data.get("name"),
            metadata=dict(data.get("metadata", {}) or {}),
        )


@dataclass(frozen=True)
class OperatorPipeline:
    """Ordered declarative pipeline of operator stages."""

    stages: list[OperatorStage] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.stages, list):
            raise ValueError("OperatorPipeline.stages must be a list.")
        if not self.stages:
            raise ValueError("OperatorPipeline.stages must be non-empty.")
        for stage in self.stages:
            if not isinstance(stage, OperatorStage):
                raise ValueError("OperatorPipeline.stages must contain OperatorStage values.")
        keys = [stage.key for stage in self.stages]
        if len(keys) != len(set(keys)):
            raise ValueError("OperatorPipeline.stages must contain unique stage keys.")
        if not isinstance(self.metadata, dict):
            raise ValueError("OperatorPipeline.metadata must be an object.")

    def stage_keys(self) -> tuple[str, ...]:
        return tuple(stage.key for stage in self.stages)

    def to_dict(self) -> dict[str, Any]:
        return {
            "stages": [_to_primitive(stage) for stage in self.stages],
            "metadata": _to_primitive(self.metadata),
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), sort_keys=True, separators=(",", ":"))

    def stable_hash(self) -> str:
        return hashlib.sha256(self.to_json().encode("utf-8")).hexdigest()

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "OperatorPipeline":
        raw_stages = list(data.get("stages", []) or [])
        return cls(
            stages=[OperatorStage.from_dict(s) if isinstance(s, dict) else s for s in raw_stages],
            metadata=dict(data.get("metadata", {}) or {}),
        )


def default_operator_pipeline() -> OperatorPipeline:
    """Return the normative V3 operator pipeline declaration."""

    return OperatorPipeline(
        stages=[OperatorStage(key=stage_key) for stage_key in NORMATIVE_STAGE_ORDER],
        metadata={"normative": True, "version": "3.4.5"},
    )
