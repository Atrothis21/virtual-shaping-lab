"""Typed temporal basis contracts for V3 representation semantics."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any

SUPPORTED_TEMPORAL_BASIS_VARIANTS: tuple[str, ...] = ("identity", "binned", "trace")


def _normalize_mapping(value: Any, field_name: str) -> dict[str, Any]:
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise ValueError(f"{field_name} must be an object.")
    return dict(value)


@dataclass(frozen=True)
class TemporalBasisSpec:
    """Typed temporal basis declaration for representation-time semantics."""

    variant: str = "identity"
    dimension: int = 1
    enabled: bool = False
    params: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        variant = str(self.variant or "").strip()
        if not variant:
            raise ValueError("TemporalBasisSpec.variant must be a non-empty string.")
        if variant not in SUPPORTED_TEMPORAL_BASIS_VARIANTS:
            supported = ", ".join(SUPPORTED_TEMPORAL_BASIS_VARIANTS)
            raise ValueError(
                f"TemporalBasisSpec.variant '{variant}' is unsupported. Supported variants: {supported}"
            )
        dimension = int(self.dimension)
        if dimension < 0:
            raise ValueError("TemporalBasisSpec.dimension must be >= 0.")
        enabled = bool(self.enabled)
        if enabled and dimension <= 0:
            raise ValueError("TemporalBasisSpec.dimension must be > 0 when enabled=True.")
        object.__setattr__(self, "variant", variant)
        object.__setattr__(self, "dimension", dimension)
        object.__setattr__(self, "enabled", enabled)
        object.__setattr__(self, "params", _normalize_mapping(self.params, "TemporalBasisSpec.params"))

    def to_dict(self) -> dict[str, Any]:
        return {
            "variant": self.variant,
            "dimension": int(self.dimension),
            "enabled": bool(self.enabled),
            "params": dict(self.params),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "TemporalBasisSpec":
        return cls(
            variant=data.get("variant", "identity"),
            dimension=int(data.get("dimension", 1)),
            enabled=bool(data.get("enabled", False)),
            params=data.get("params", {}),
        )

    def stable_hash(self) -> str:
        blob = json.dumps(self.to_dict(), sort_keys=True, separators=(",", ":")).encode("utf-8")
        return hashlib.sha256(blob).hexdigest()

