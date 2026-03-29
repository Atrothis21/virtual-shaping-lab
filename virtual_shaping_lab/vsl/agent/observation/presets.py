"""Named observation preset registry and deterministic expansion."""

from __future__ import annotations

import hashlib
import json
from typing import Any

from .spec import ObservationSpec

PRESET_VERSION = "3.19.0"

OBSERVATION_PRESETS: dict[str, tuple[str, str, str]] = {
    "classical_identity": ("identity", "none", "none"),
    "operant_vector": ("stimulus_vector", "discrete_context", "stimulus_similarity"),
    "contextual_basis": ("temporal_basis", "discrete_context", "context_gate"),
    "latent_context_basis": ("temporal_basis", "latent_context", "context_gate"),
}

OBSERVATION_PRESET_ALIASES: dict[str, str] = {
    "rw_classical": "classical_identity",
    "q_operant": "operant_vector",
}

OBSERVATION_PRESET_FAMILIES: dict[str, list[str]] = {
    "classical": ["classical_identity"],
    "operant": ["operant_vector", "contextual_basis", "latent_context_basis"],
}


def _resolve_preset_name(name: str) -> str:
    key = str(name).strip()
    if key in OBSERVATION_PRESETS:
        return key
    alias_target = OBSERVATION_PRESET_ALIASES.get(key)
    if alias_target is not None:
        return alias_target
    raise ValueError(f"[OBS_E_UNKNOWN_PRESET] Unknown observation preset '{name}'.")


def observation_preset_names() -> list[str]:
    return sorted(OBSERVATION_PRESETS.keys())


def observation_preset_aliases() -> dict[str, str]:
    return {key: OBSERVATION_PRESET_ALIASES[key] for key in sorted(OBSERVATION_PRESET_ALIASES.keys())}


def observation_preset_registry() -> dict[str, list[str]]:
    return {name: list(OBSERVATION_PRESETS[name]) for name in sorted(OBSERVATION_PRESETS.keys())}


def observation_preset_families() -> dict[str, list[str]]:
    return {family: list(names) for family, names in sorted(OBSERVATION_PRESET_FAMILIES.items())}


def expand_observation_preset(name: str, *, metadata: dict[str, Any] | None = None) -> ObservationSpec:
    resolved_name = _resolve_preset_name(name)
    representation, context, generalization = OBSERVATION_PRESETS[resolved_name]
    merged_metadata = {
        "preset_name": resolved_name,
        "preset_version": PRESET_VERSION,
    }
    if metadata:
        merged_metadata.update(dict(metadata))
    return ObservationSpec(
        representation=representation,
        context=context,
        generalization=generalization,
        metadata=merged_metadata,
    )


def observation_preset_payload(name: str, *, metadata: dict[str, Any] | None = None) -> dict[str, Any]:
    spec = expand_observation_preset(name, metadata=metadata)
    return {
        "preset_name": spec.metadata.get("preset_name"),
        "spec": spec.to_dict(),
        "registry_version": PRESET_VERSION,
    }


def observation_preset_hash(name: str, *, metadata: dict[str, Any] | None = None) -> str:
    blob = json.dumps(observation_preset_payload(name, metadata=metadata), sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()

