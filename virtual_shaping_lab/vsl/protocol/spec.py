"""Typed protocol-grammar declaration for V3.21."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any

from .validation import validate_protocol_spec


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
class ProtocolSpec:
    """Declarative protocol grammar for experiment-side dynamics."""

    emission_rule: str
    consequence_rule: str
    advance_rule: str
    stop_rule: str
    protocol_family: str
    action_space_mode: str
    temporal_mode: str
    schedule_metadata: dict[str, Any] = field(default_factory=dict)
    phase_metadata: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "emission_rule",
            _require_non_empty_string(self.emission_rule, "ProtocolSpec.emission_rule"),
        )
        object.__setattr__(
            self,
            "consequence_rule",
            _require_non_empty_string(self.consequence_rule, "ProtocolSpec.consequence_rule"),
        )
        object.__setattr__(
            self,
            "advance_rule",
            _require_non_empty_string(self.advance_rule, "ProtocolSpec.advance_rule"),
        )
        object.__setattr__(
            self,
            "stop_rule",
            _require_non_empty_string(self.stop_rule, "ProtocolSpec.stop_rule"),
        )
        object.__setattr__(
            self,
            "protocol_family",
            _require_non_empty_string(self.protocol_family, "ProtocolSpec.protocol_family"),
        )
        object.__setattr__(
            self,
            "action_space_mode",
            _require_non_empty_string(self.action_space_mode, "ProtocolSpec.action_space_mode"),
        )
        object.__setattr__(
            self,
            "temporal_mode",
            _require_non_empty_string(self.temporal_mode, "ProtocolSpec.temporal_mode"),
        )
        if not isinstance(self.schedule_metadata, dict):
            raise ValueError("ProtocolSpec.schedule_metadata must be an object.")
        if not isinstance(self.phase_metadata, dict):
            raise ValueError("ProtocolSpec.phase_metadata must be an object.")
        if not isinstance(self.metadata, dict):
            raise ValueError("ProtocolSpec.metadata must be an object.")
        object.__setattr__(self, "schedule_metadata", dict(self.schedule_metadata))
        object.__setattr__(self, "phase_metadata", dict(self.phase_metadata))
        object.__setattr__(self, "metadata", dict(self.metadata))
        validate_protocol_spec(self)

    def to_dict(self) -> dict[str, Any]:
        return {
            "emission_rule": self.emission_rule,
            "consequence_rule": self.consequence_rule,
            "advance_rule": self.advance_rule,
            "stop_rule": self.stop_rule,
            "protocol_family": self.protocol_family,
            "action_space_mode": self.action_space_mode,
            "temporal_mode": self.temporal_mode,
            "schedule_metadata": _to_primitive(self.schedule_metadata),
            "phase_metadata": _to_primitive(self.phase_metadata),
            "metadata": _to_primitive(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ProtocolSpec":
        return cls(
            emission_rule=data.get("emission_rule", ""),
            consequence_rule=data.get("consequence_rule", ""),
            advance_rule=data.get("advance_rule", ""),
            stop_rule=data.get("stop_rule", ""),
            protocol_family=data.get("protocol_family", ""),
            action_space_mode=data.get("action_space_mode", ""),
            temporal_mode=data.get("temporal_mode", ""),
            schedule_metadata=data.get("schedule_metadata", {}),
            phase_metadata=data.get("phase_metadata", {}),
            metadata=data.get("metadata", {}),
        )

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), sort_keys=True, separators=(",", ":"))

    def stable_hash(self) -> str:
        return hashlib.sha256(self.to_json().encode("utf-8")).hexdigest()
