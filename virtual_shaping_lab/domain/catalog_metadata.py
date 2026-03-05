"""Shared UI-facing catalog metadata contracts."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


def _default_label(key: str) -> str:
    parts = [p for p in key.replace("-", "_").split("_") if p]
    if not parts:
        return key
    return " ".join(p.capitalize() for p in parts)


@dataclass(frozen=True)
class UICatalogMetadata:
    """UI-discovery metadata carried by catalog entries."""

    label: str
    description: str
    params_schema: dict[str, Any] = field(default_factory=dict)
    defaults: dict[str, Any] = field(default_factory=dict)
    constraints: tuple[str, ...] = ()
    examples: tuple[dict[str, Any], ...] = ()


def make_default_ui_metadata(key: str, *, description_prefix: str) -> UICatalogMetadata:
    label = _default_label(key)
    return UICatalogMetadata(
        label=label,
        description=f"{description_prefix}: {label}.",
        params_schema={},
        defaults={},
        constraints=(),
        examples=(),
    )


def validate_ui_metadata_map(
    *,
    keys: set[str],
    metadata_map: dict[str, UICatalogMetadata],
    namespace: str,
) -> None:
    missing = sorted(keys - set(metadata_map))
    extra = sorted(set(metadata_map) - keys)
    if missing:
        raise ValueError(f"{namespace}: missing metadata for keys: {', '.join(missing)}")
    if extra:
        raise ValueError(f"{namespace}: metadata contains unknown keys: {', '.join(extra)}")

    for key, meta in metadata_map.items():
        if not isinstance(meta, UICatalogMetadata):
            raise ValueError(f"{namespace}: metadata for '{key}' must be UICatalogMetadata.")
        if not isinstance(meta.label, str) or not meta.label.strip():
            raise ValueError(f"{namespace}: metadata '{key}' must include non-empty label.")
        if not isinstance(meta.description, str) or not meta.description.strip():
            raise ValueError(f"{namespace}: metadata '{key}' must include non-empty description.")
        if not isinstance(meta.params_schema, dict):
            raise ValueError(f"{namespace}: metadata '{key}' params_schema must be a dict.")
        if not isinstance(meta.defaults, dict):
            raise ValueError(f"{namespace}: metadata '{key}' defaults must be a dict.")
        if not isinstance(meta.constraints, tuple) or not all(isinstance(v, str) for v in meta.constraints):
            raise ValueError(f"{namespace}: metadata '{key}' constraints must be tuple[str, ...].")
        if not isinstance(meta.examples, tuple) or not all(isinstance(v, dict) for v in meta.examples):
            raise ValueError(f"{namespace}: metadata '{key}' examples must be tuple[dict[str, Any], ...].")
