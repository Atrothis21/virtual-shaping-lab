"""Machine-readable learner slot registries and compatibility matrix."""

from __future__ import annotations

import hashlib
import json
from typing import Any

from .validation import (
    ACTOR_CRITIC_REQUIRED,
    ATTENTION_TO_UPDATERS_STRICT,
    ATTENTION_VALUES,
    ERROR_VALUES,
    ERROR_REQUIRES_ACTION_POLICY,
    ERROR_REQUIRES_Q_PREDICTOR,
    EXPECTED_SARSA_POLICIES,
    POLICY_VALUES,
    POLICY_NONE_INCOMPATIBLE_PREDICTORS,
    PREDICTOR_TO_ERRORS,
    PREDICTOR_TO_POLICIES,
    PREDICTOR_VALUES,
    TRACE_TO_UPDATERS,
    TRACE_VALUES,
    UPDATER_VALUES,
)


def _sorted_mapping(source: dict[str, set[str]]) -> dict[str, list[str]]:
    return {key: sorted(source[key]) for key in sorted(source.keys())}


SLOT_REGISTRIES: dict[str, list[str]] = {
    "trace": sorted(TRACE_VALUES),
    "predictor": sorted(PREDICTOR_VALUES),
    "error": sorted(ERROR_VALUES),
    "attention": sorted(ATTENTION_VALUES),
    "updater": sorted(UPDATER_VALUES),
    "policy": sorted(POLICY_VALUES),
}


COMPATIBILITY_MATRIX: dict[str, dict[str, list[str]]] = {
    "predictor_to_error": _sorted_mapping(PREDICTOR_TO_ERRORS),
    "predictor_to_policy": _sorted_mapping(PREDICTOR_TO_POLICIES),
    "trace_to_updater": _sorted_mapping(TRACE_TO_UPDATERS),
    "attention_to_updater_strict": _sorted_mapping(ATTENTION_TO_UPDATERS_STRICT),
    "error_requires_q_predictor": {
        "errors": sorted(ERROR_REQUIRES_Q_PREDICTOR),
        "allowed_predictors": ["nonlinear_q", "q_value"],
    },
    "error_requires_action_policy": {
        "errors": sorted(ERROR_REQUIRES_ACTION_POLICY),
        "forbidden_policy": ["none"],
    },
    "expected_sarsa_policy": {
        "error": ["expected_sarsa_error"],
        "allowed_policies": sorted(EXPECTED_SARSA_POLICIES),
    },
    "policy_none_incompatible_predictors": {
        "predictors": sorted(POLICY_NONE_INCOMPATIBLE_PREDICTORS),
        "policy": ["none"],
    },
    "actor_critic_required": {
        "predictor": [ACTOR_CRITIC_REQUIRED["predictor"]],
        "error": [ACTOR_CRITIC_REQUIRED["error"]],
        "updater": [ACTOR_CRITIC_REQUIRED["updater"]],
        "policy": [ACTOR_CRITIC_REQUIRED["policy"]],
    },
}


def slot_registries() -> dict[str, list[str]]:
    return {slot: list(values) for slot, values in SLOT_REGISTRIES.items()}


def compatibility_matrix() -> dict[str, dict[str, list[str]]]:
    return {
        section: {key: list(values) for key, values in mapping.items()}
        for section, mapping in COMPATIBILITY_MATRIX.items()
    }


def learner_registry_payload() -> dict[str, Any]:
    return {
        "slot_registries": slot_registries(),
        "compatibility_matrix": compatibility_matrix(),
        "version": "3.5.0",
    }


def learner_registry_hash() -> str:
    blob = json.dumps(learner_registry_payload(), sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()
