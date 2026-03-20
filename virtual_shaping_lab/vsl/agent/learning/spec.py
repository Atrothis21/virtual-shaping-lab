"""Typed learner-grammar declaration for V3."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any

from .validator import validate_learner_spec


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
class LearnerSpec:
    """
    Declarative learner grammar.

    The grammar is intentionally slot-oriented so legality validation can be
    layered on later without changing the type boundary.
    """

    trace: str
    predictor: str
    error: str
    attention: str
    updater: str
    policy: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "trace", _require_non_empty_string(self.trace, "LearnerSpec.trace"))
        object.__setattr__(self, "predictor", _require_non_empty_string(self.predictor, "LearnerSpec.predictor"))
        object.__setattr__(self, "error", _require_non_empty_string(self.error, "LearnerSpec.error"))
        object.__setattr__(self, "attention", _require_non_empty_string(self.attention, "LearnerSpec.attention"))
        object.__setattr__(self, "updater", _require_non_empty_string(self.updater, "LearnerSpec.updater"))
        object.__setattr__(self, "policy", _require_non_empty_string(self.policy, "LearnerSpec.policy"))
        if not isinstance(self.metadata, dict):
            raise ValueError("LearnerSpec.metadata must be an object.")
        object.__setattr__(self, "metadata", dict(self.metadata))
        validate_learner_spec(self)

    def to_dict(self) -> dict[str, Any]:
        return {
            "trace": self.trace,
            "predictor": self.predictor,
            "error": self.error,
            "attention": self.attention,
            "updater": self.updater,
            "policy": self.policy,
            "metadata": _to_primitive(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "LearnerSpec":
        return cls(
            trace=data.get("trace", ""),
            predictor=data.get("predictor", ""),
            error=data.get("error", ""),
            attention=data.get("attention", ""),
            updater=data.get("updater", ""),
            policy=data.get("policy", ""),
            metadata=data.get("metadata", {}),
        )

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), sort_keys=True, separators=(",", ":"))

    def stable_hash(self) -> str:
        return hashlib.sha256(self.to_json().encode("utf-8")).hexdigest()
