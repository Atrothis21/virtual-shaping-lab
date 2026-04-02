"""Typed measurement-grammar declaration for V3.22."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any


def _to_primitive(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(k): _to_primitive(v) for k, v in sorted(value.items(), key=lambda item: str(item[0]))}
    if isinstance(value, list):
        return [_to_primitive(v) for v in value]
    if isinstance(value, tuple):
        return [_to_primitive(v) for v in value]
    return value


def _normalize_string_list(values: Any, field_name: str) -> list[str]:
    if not isinstance(values, (list, tuple)):
        raise ValueError(f"{field_name} must be a list of non-empty strings.")
    normalized: list[str] = []
    for value in values:
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{field_name} must be a list of non-empty strings.")
        normalized.append(value.strip())
    return normalized


def _require_non_empty_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} must be a non-empty string.")
    return value.strip()


@dataclass(frozen=True)
class MeasurementSpec:
    """Declarative measurement grammar for post-rollout analysis surfaces."""

    analysis_ops: list[str] = field(default_factory=list)
    visualization_ops: list[str] = field(default_factory=list)
    report_op: str = "default_report"
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "analysis_ops",
            _normalize_string_list(self.analysis_ops, "MeasurementSpec.analysis_ops"),
        )
        object.__setattr__(
            self,
            "visualization_ops",
            _normalize_string_list(self.visualization_ops, "MeasurementSpec.visualization_ops"),
        )
        object.__setattr__(
            self,
            "report_op",
            _require_non_empty_string(self.report_op, "MeasurementSpec.report_op"),
        )
        if not isinstance(self.metadata, dict):
            raise ValueError("MeasurementSpec.metadata must be an object.")
        object.__setattr__(self, "metadata", dict(self.metadata))

    def to_dict(self) -> dict[str, Any]:
        return {
            "analysis_ops": _to_primitive(self.analysis_ops),
            "visualization_ops": _to_primitive(self.visualization_ops),
            "report_op": self.report_op,
            "metadata": _to_primitive(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "MeasurementSpec":
        return cls(
            analysis_ops=data.get("analysis_ops", []),
            visualization_ops=data.get("visualization_ops", []),
            report_op=data.get("report_op", "default_report"),
            metadata=data.get("metadata", {}),
        )

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), sort_keys=True, separators=(",", ":"))

    def stable_hash(self) -> str:
        return hashlib.sha256(self.to_json().encode("utf-8")).hexdigest()
