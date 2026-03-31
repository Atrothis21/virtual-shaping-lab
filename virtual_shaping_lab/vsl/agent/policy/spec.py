"""Typed policy-grammar declaration for V3.20."""

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


def _require_non_empty_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} must be a non-empty string.")
    return value.strip()


@dataclass(frozen=True)
class PolicySpec:
    """Declarative policy grammar for action selection behavior."""

    selection_rule: str
    action_space_mode: str
    parameters: dict[str, Any] = field(default_factory=dict)
    tie_break_rule: str | None = None
    availability_rule: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "selection_rule",
            _require_non_empty_string(self.selection_rule, "PolicySpec.selection_rule"),
        )
        object.__setattr__(
            self,
            "action_space_mode",
            _require_non_empty_string(self.action_space_mode, "PolicySpec.action_space_mode"),
        )
        if self.tie_break_rule is not None:
            object.__setattr__(
                self,
                "tie_break_rule",
                _require_non_empty_string(self.tie_break_rule, "PolicySpec.tie_break_rule"),
            )
        if self.availability_rule is not None:
            object.__setattr__(
                self,
                "availability_rule",
                _require_non_empty_string(self.availability_rule, "PolicySpec.availability_rule"),
            )
        if not isinstance(self.parameters, dict):
            raise ValueError("PolicySpec.parameters must be an object.")
        if not isinstance(self.metadata, dict):
            raise ValueError("PolicySpec.metadata must be an object.")
        object.__setattr__(self, "parameters", dict(self.parameters))
        object.__setattr__(self, "metadata", dict(self.metadata))

    def to_dict(self) -> dict[str, Any]:
        return {
            "selection_rule": self.selection_rule,
            "action_space_mode": self.action_space_mode,
            "parameters": _to_primitive(self.parameters),
            "tie_break_rule": self.tie_break_rule,
            "availability_rule": self.availability_rule,
            "metadata": _to_primitive(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "PolicySpec":
        return cls(
            selection_rule=data.get("selection_rule", ""),
            action_space_mode=data.get("action_space_mode", ""),
            parameters=data.get("parameters", {}),
            tie_break_rule=data.get("tie_break_rule"),
            availability_rule=data.get("availability_rule"),
            metadata=data.get("metadata", {}),
        )

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), sort_keys=True, separators=(",", ":"))

    def stable_hash(self) -> str:
        return hashlib.sha256(self.to_json().encode("utf-8")).hexdigest()

