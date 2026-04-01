"""Named protocol preset registry and deterministic expansion."""

from __future__ import annotations

import hashlib
import json
from typing import Any

from .spec import ProtocolSpec

PRESET_VERSION = "3.21.0"

PROTOCOL_PRESETS: dict[str, dict[str, Any]] = {
    "classical_acquisition": {
        "emission_rule": "classical_trial_emission",
        "consequence_rule": "deterministic_consequence",
        "advance_rule": "trial_increment",
        "stop_rule": "n_trials",
        "protocol_family": "acquisition",
        "action_space_mode": "classical_none",
        "temporal_mode": "trial_discrete",
    },
    "classical_extinction": {
        "emission_rule": "classical_trial_emission",
        "consequence_rule": "null_consequence",
        "advance_rule": "trial_increment",
        "stop_rule": "n_trials",
        "protocol_family": "extinction",
        "action_space_mode": "classical_none",
        "temporal_mode": "trial_discrete",
    },
    "operant_trial_discrete": {
        "emission_rule": "operant_offer_emission",
        "consequence_rule": "scheduled_consequence",
        "advance_rule": "trial_increment",
        "stop_rule": "n_trials",
        "protocol_family": "operant_conditioning",
        "action_space_mode": "discrete",
        "temporal_mode": "trial_discrete",
    },
    "operant_binary_response": {
        "emission_rule": "operant_offer_emission",
        "consequence_rule": "deterministic_consequence",
        "advance_rule": "trial_increment",
        "stop_rule": "n_trials",
        "protocol_family": "operant_conditioning",
        "action_space_mode": "binary_response",
        "temporal_mode": "trial_discrete",
    },
}

PROTOCOL_PRESET_ALIASES: dict[str, str] = {
    "acquisition": "classical_acquisition",
    "extinction": "classical_extinction",
    "operant": "operant_trial_discrete",
}

PROTOCOL_PRESET_FAMILIES: dict[str, list[str]] = {
    "classical": ["classical_acquisition", "classical_extinction"],
    "operant": ["operant_trial_discrete", "operant_binary_response"],
}


def _resolve_preset_name(name: str) -> str:
    key = str(name).strip()
    if key in PROTOCOL_PRESETS:
        return key
    alias_target = PROTOCOL_PRESET_ALIASES.get(key)
    if alias_target is not None:
        return alias_target
    raise ValueError(f"[PROTO_E_UNKNOWN_PRESET] Unknown protocol preset '{name}'.")


def protocol_preset_names() -> list[str]:
    return sorted(PROTOCOL_PRESETS.keys())


def protocol_preset_aliases() -> dict[str, str]:
    return {key: PROTOCOL_PRESET_ALIASES[key] for key in sorted(PROTOCOL_PRESET_ALIASES.keys())}


def protocol_preset_registry() -> dict[str, dict[str, Any]]:
    return {name: dict(PROTOCOL_PRESETS[name]) for name in sorted(PROTOCOL_PRESETS.keys())}


def protocol_preset_families() -> dict[str, list[str]]:
    return {family: list(names) for family, names in sorted(PROTOCOL_PRESET_FAMILIES.items())}


def expand_protocol_preset(name: str, *, metadata: dict[str, Any] | None = None) -> ProtocolSpec:
    resolved_name = _resolve_preset_name(name)
    preset = PROTOCOL_PRESETS[resolved_name]
    merged_metadata: dict[str, Any] = {
        "preset_name": resolved_name,
        "preset_version": PRESET_VERSION,
    }
    if metadata:
        merged_metadata.update(dict(metadata))
    return ProtocolSpec(
        emission_rule=preset["emission_rule"],
        consequence_rule=preset["consequence_rule"],
        advance_rule=preset["advance_rule"],
        stop_rule=preset["stop_rule"],
        protocol_family=preset["protocol_family"],
        action_space_mode=preset["action_space_mode"],
        temporal_mode=preset["temporal_mode"],
        metadata=merged_metadata,
    )


def protocol_preset_payload(name: str, *, metadata: dict[str, Any] | None = None) -> dict[str, Any]:
    spec = expand_protocol_preset(name, metadata=metadata)
    return {
        "preset_name": spec.metadata.get("preset_name"),
        "spec": spec.to_dict(),
        "registry_version": PRESET_VERSION,
    }


def protocol_preset_hash(name: str, *, metadata: dict[str, Any] | None = None) -> str:
    blob = json.dumps(protocol_preset_payload(name, metadata=metadata), sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()
