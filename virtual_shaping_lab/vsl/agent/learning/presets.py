"""Named learner preset registry and deterministic expansion."""

from __future__ import annotations

import hashlib
import json
from typing import Any

from .spec import LearnerSpec

PRESET_VERSION = "3.5.0"

LEARNER_PRESETS: dict[str, tuple[str, str, str, str, str, str]] = {
    "rw": ("none", "state_value", "rw_error", "fixed", "delta_rule", "none"),
    "td0_classical": ("none", "state_value", "td_error", "fixed", "delta_rule", "none"),
    "td_lambda_classical": ("eligibility", "state_value", "td_error", "fixed", "trace_delta_rule", "none"),
    "sarsa": ("none", "q_value", "sarsa_error", "fixed", "delta_rule", "epsilon_greedy"),
    "q_learning": ("none", "q_value", "q_error", "fixed", "delta_rule", "epsilon_greedy"),
    "expected_sarsa": ("none", "q_value", "expected_sarsa_error", "fixed", "delta_rule", "softmax"),
    "actor_critic": ("none", "actor_critic_pair", "actor_critic_td_error", "fixed", "actor_critic_update", "actor_policy"),
    "actor_critic_lambda": (
        "eligibility",
        "actor_critic_pair",
        "actor_critic_td_error",
        "fixed",
        "actor_critic_update",
        "actor_policy",
    ),
}

LEARNER_PRESET_ALIASES: dict[str, str] = {
    "rescorla_wagner": "rw",
    "td0": "td0_classical",
    "q_learning_softmax": "expected_sarsa",
}

LEARNER_PRESET_FAMILIES: dict[str, list[str]] = {
    "classical": ["rw", "td0_classical", "td_lambda_classical"],
    "operant_value": ["sarsa", "q_learning", "expected_sarsa"],
}


def _resolve_preset_name(name: str) -> str:
    key = str(name).strip()
    if key in LEARNER_PRESETS:
        return key
    alias_target = LEARNER_PRESET_ALIASES.get(key)
    if alias_target is not None:
        return alias_target
    raise ValueError(f"[LGR_E_UNKNOWN_PRESET] Unknown learner preset '{name}'.")


def learner_preset_names() -> list[str]:
    return sorted(LEARNER_PRESETS.keys())


def learner_preset_aliases() -> dict[str, str]:
    return {k: LEARNER_PRESET_ALIASES[k] for k in sorted(LEARNER_PRESET_ALIASES.keys())}


def learner_preset_registry() -> dict[str, list[str]]:
    return {name: list(LEARNER_PRESETS[name]) for name in sorted(LEARNER_PRESETS.keys())}


def learner_preset_families() -> dict[str, list[str]]:
    return {family: list(names) for family, names in sorted(LEARNER_PRESET_FAMILIES.items())}


def expand_learner_preset(name: str, *, metadata: dict[str, Any] | None = None) -> LearnerSpec:
    resolved_name = _resolve_preset_name(name)
    trace, predictor, error, attention, updater, policy = LEARNER_PRESETS[resolved_name]
    merged_metadata = {
        "preset_name": resolved_name,
        "preset_version": PRESET_VERSION,
    }
    if metadata:
        merged_metadata.update(dict(metadata))
    return LearnerSpec(
        trace=trace,
        predictor=predictor,
        error=error,
        attention=attention,
        updater=updater,
        policy=policy,
        metadata=merged_metadata,
    )


def learner_preset_payload(name: str, *, metadata: dict[str, Any] | None = None) -> dict[str, Any]:
    spec = expand_learner_preset(name, metadata=metadata)
    return {
        "preset_name": spec.metadata.get("preset_name"),
        "spec": spec.to_dict(),
        "registry_version": PRESET_VERSION,
    }


def learner_preset_hash(name: str, *, metadata: dict[str, Any] | None = None) -> str:
    blob = json.dumps(learner_preset_payload(name, metadata=metadata), sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()

