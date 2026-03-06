"""Shared UI-facing catalog metadata contracts."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

# Canonical, machine-checkable UI constraint symbols.
CONSTRAINT_PAVLOVIAN_ONLY = "pavlovian_only"
CONSTRAINT_OPERANT_ONLY = "operant_only"
CONSTRAINT_REQUIRES_COMPOUND_STIMULI = "requires_compound_stimuli"
CONSTRAINT_REQUIRES_CS_PLUS_CS_MINUS_STIMULI = "requires_cs_plus_cs_minus_stimuli"
CONSTRAINT_REQUIRES_COMPOUND_TRIALS = "requires_compound_trials"
CONSTRAINT_LEARNING_DISABLED_DEFAULT = "learning_disabled_default"
CONSTRAINT_CONTROL_FLOW_PHASE = "control_flow_phase"
CONSTRAINT_TEMPLATE_PHASE = "template_phase"
CONSTRAINT_TEMPLATE_ALIAS = "template_alias"
CONSTRAINT_CONTEXT_SHIFT_PROTOCOL = "context_shift_protocol"
CONSTRAINT_CONCURRENT_SCHEDULE = "concurrent_schedule"
CONSTRAINT_ANALYSIS_DEFAULT_TEMPLATE = "analysis_default_template"
CONSTRAINT_FALLBACK_TEMPLATE = "fallback_template"
CONSTRAINT_ACQUISITION_COMPATIBLE = "acquisition_compatible"
CONSTRAINT_EXTINCTION_COMPATIBLE = "extinction_compatible"
CONSTRAINT_CUE_COMPETITION_COMPATIBLE = "cue_competition_compatible"
CONSTRAINT_INHIBITION_COMPATIBLE = "inhibition_compatible"
CONSTRAINT_RENEWAL_COMPATIBLE = "renewal_compatible"
CONSTRAINT_OPERANT_COMPATIBLE = "operant_compatible"

ALLOWED_UI_CONSTRAINTS: frozenset[str] = frozenset(
    {
        CONSTRAINT_PAVLOVIAN_ONLY,
        CONSTRAINT_OPERANT_ONLY,
        CONSTRAINT_REQUIRES_COMPOUND_STIMULI,
        CONSTRAINT_REQUIRES_CS_PLUS_CS_MINUS_STIMULI,
        CONSTRAINT_REQUIRES_COMPOUND_TRIALS,
        CONSTRAINT_LEARNING_DISABLED_DEFAULT,
        CONSTRAINT_CONTROL_FLOW_PHASE,
        CONSTRAINT_TEMPLATE_PHASE,
        CONSTRAINT_TEMPLATE_ALIAS,
        CONSTRAINT_CONTEXT_SHIFT_PROTOCOL,
        CONSTRAINT_CONCURRENT_SCHEDULE,
        CONSTRAINT_ANALYSIS_DEFAULT_TEMPLATE,
        CONSTRAINT_FALLBACK_TEMPLATE,
        CONSTRAINT_ACQUISITION_COMPATIBLE,
        CONSTRAINT_EXTINCTION_COMPATIBLE,
        CONSTRAINT_CUE_COMPETITION_COMPATIBLE,
        CONSTRAINT_INHIBITION_COMPATIBLE,
        CONSTRAINT_RENEWAL_COMPATIBLE,
        CONSTRAINT_OPERANT_COMPATIBLE,
    }
)


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
        unknown_constraints = sorted(c for c in meta.constraints if c not in ALLOWED_UI_CONSTRAINTS)
        if unknown_constraints:
            raise ValueError(
                f"{namespace}: metadata '{key}' contains unknown constraints: {', '.join(unknown_constraints)}"
            )
        if not isinstance(meta.examples, tuple) or not all(isinstance(v, dict) for v in meta.examples):
            raise ValueError(f"{namespace}: metadata '{key}' examples must be tuple[dict[str, Any], ...].")
