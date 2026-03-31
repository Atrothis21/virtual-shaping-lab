"""Named policy preset registry and deterministic expansion."""

from __future__ import annotations

import hashlib
import json
from typing import Any

from .spec import PolicySpec

PRESET_VERSION = "3.20.0"

POLICY_PRESETS: dict[str, dict[str, Any]] = {
    "classical_none": {
        "selection_rule": "null",
        "action_space_mode": "classical_none",
        "parameters": {},
        "tie_break_rule": "stable_lexicographic",
        "availability_rule": "none",
    },
    "operant_greedy": {
        "selection_rule": "greedy",
        "action_space_mode": "discrete",
        "parameters": {},
        "tie_break_rule": "stable_lexicographic",
        "availability_rule": "environment_declared",
    },
    "operant_epsilon_greedy": {
        "selection_rule": "epsilon_greedy",
        "action_space_mode": "discrete",
        "parameters": {"epsilon": 0.1},
        "tie_break_rule": "random",
        "availability_rule": "environment_declared",
    },
    "operant_softmax": {
        "selection_rule": "softmax",
        "action_space_mode": "discrete",
        "parameters": {"temperature": 1.0},
        "tie_break_rule": "random",
        "availability_rule": "environment_declared",
    },
    "operant_uniform_random": {
        "selection_rule": "uniform_random",
        "action_space_mode": "discrete",
        "parameters": {},
        "tie_break_rule": "random",
        "availability_rule": "environment_declared",
    },
}

POLICY_PRESET_ALIASES: dict[str, str] = {
    "no_policy": "classical_none",
    "greedy": "operant_greedy",
    "epsilon_greedy": "operant_epsilon_greedy",
    "softmax": "operant_softmax",
    "uniform_random": "operant_uniform_random",
}

POLICY_PRESET_FAMILIES: dict[str, list[str]] = {
    "classical": ["classical_none"],
    "operant": [
        "operant_greedy",
        "operant_epsilon_greedy",
        "operant_softmax",
        "operant_uniform_random",
    ],
}


def _resolve_preset_name(name: str) -> str:
    key = str(name).strip()
    if key in POLICY_PRESETS:
        return key
    alias_target = POLICY_PRESET_ALIASES.get(key)
    if alias_target is not None:
        return alias_target
    raise ValueError(f"[POL_E_UNKNOWN_PRESET] Unknown policy preset '{name}'.")


def policy_preset_names() -> list[str]:
    return sorted(POLICY_PRESETS.keys())


def policy_preset_aliases() -> dict[str, str]:
    return {key: POLICY_PRESET_ALIASES[key] for key in sorted(POLICY_PRESET_ALIASES.keys())}


def policy_preset_registry() -> dict[str, dict[str, Any]]:
    return {name: dict(POLICY_PRESETS[name]) for name in sorted(POLICY_PRESETS.keys())}


def policy_preset_families() -> dict[str, list[str]]:
    return {family: list(names) for family, names in sorted(POLICY_PRESET_FAMILIES.items())}


def expand_policy_preset(name: str, *, metadata: dict[str, Any] | None = None) -> PolicySpec:
    resolved_name = _resolve_preset_name(name)
    preset = POLICY_PRESETS[resolved_name]
    merged_metadata: dict[str, Any] = {
        "preset_name": resolved_name,
        "preset_version": PRESET_VERSION,
    }
    if metadata:
        merged_metadata.update(dict(metadata))
    return PolicySpec(
        selection_rule=preset["selection_rule"],
        action_space_mode=preset["action_space_mode"],
        parameters=dict(preset.get("parameters", {})),
        tie_break_rule=preset.get("tie_break_rule"),
        availability_rule=preset.get("availability_rule"),
        metadata=merged_metadata,
    )


def policy_preset_payload(name: str, *, metadata: dict[str, Any] | None = None) -> dict[str, Any]:
    spec = expand_policy_preset(name, metadata=metadata)
    return {
        "preset_name": spec.metadata.get("preset_name"),
        "spec": spec.to_dict(),
        "registry_version": PRESET_VERSION,
    }


def policy_preset_hash(name: str, *, metadata: dict[str, Any] | None = None) -> str:
    blob = json.dumps(policy_preset_payload(name, metadata=metadata), sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()

