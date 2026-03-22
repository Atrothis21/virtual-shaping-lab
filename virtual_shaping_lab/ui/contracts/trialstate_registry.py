"""Canonical TrialState field registry contract for V3 UI surfaces."""

from __future__ import annotations

from copy import deepcopy
from typing import Any


class TrialStateRegistryValidationError(ValueError):
    """Raised when a TrialState field registry contract is invalid."""


TRIALSTATE_FIELD_REGISTRY_VERSION = "3.0"

REQUIRED_TRIALSTATE_FIELD_GROUPS: tuple[str, ...] = (
    "stimulus_input",
    "representation",
    "prediction",
    "outcome",
    "learning_signal",
    "update_state",
    "attention_memory",
    "action_policy",
    "evaluation",
    "metadata",
)

REQUIRED_TRIALSTATE_FIELDS: tuple[str, ...] = (
    "stimulus",
    "state",
    "prediction",
    "outcome",
    "error",
    "weights",
    "trial_index",
    "phase_name",
)


TRIALSTATE_FIELD_REGISTRY: dict[str, Any] = {
    "version": TRIALSTATE_FIELD_REGISTRY_VERSION,
    "field_groups": {
        "stimulus_input": {
            "label": "Stimulus Input",
            "description": "Presented cues, contexts, and outcomes for the current trial.",
        },
        "representation": {
            "label": "Representation",
            "description": "Internal encoded state derived from current inputs.",
        },
        "prediction": {
            "label": "Prediction",
            "description": "Expected outcomes or values produced before observing feedback.",
        },
        "outcome": {
            "label": "Outcome",
            "description": "Observed reinforcement or feedback from the environment.",
        },
        "learning_signal": {
            "label": "Learning Signal",
            "description": "Discrepancy variables that drive learning.",
        },
        "update_state": {
            "label": "Update State",
            "description": "Parameters and intermediate values involved in learning updates.",
        },
        "attention_memory": {
            "label": "Attention / Memory",
            "description": "Associability, traces, and history-carrying variables.",
        },
        "action_policy": {
            "label": "Action / Policy",
            "description": "Action and policy-related trial values.",
        },
        "evaluation": {
            "label": "Evaluation / Outputs",
            "description": "Behavioral readouts exposed downstream.",
        },
        "metadata": {
            "label": "Metadata",
            "description": "Indices and bookkeeping values for the current trial.",
        },
    },
    "visibility_policies": {
        "preset_mode_default": "hidden",
        "operator_view_allowed": ["mechanism", "operator", "expert"],
        "results_overlay_allowed": True,
    },
    "fields": {
        "stimulus": {
            "id": "stimulus",
            "label": "Stimulus",
            "group": "stimulus_input",
            "pedagogy": {
                "intuition": "The cue or cues presented on this trial.",
                "mechanism": "The raw stimulus payload before encoding.",
                "operator_view": "An input field read by representation operators.",
                "expert": "May be symbolic, structured, or multimodal.",
            },
            "runtime": {
                "kind": "object",
                "shape": "structured",
                "nullable": False,
                "default": {},
                "produced_by": [],
                "consumed_by": ["phi"],
            },
            "visibility": {
                "preset_mode": "hidden",
                "mechanism_layer": True,
                "operator_layer": True,
                "expert_mode": True,
                "results_overlay": False,
            },
        },
        "state": {
            "id": "state",
            "label": "State Representation",
            "group": "representation",
            "pedagogy": {
                "intuition": "The model's internal encoding of what is present.",
                "mechanism": "Encoded feature state produced from stimulus and context.",
                "operator_view": "Representational carrier written by representation operators.",
                "expert": "Can be sparse, dense, elemental, or configural.",
            },
            "runtime": {
                "kind": "array",
                "shape": "vector_or_structured",
                "nullable": False,
                "default": [],
                "produced_by": ["phi", "g", "c"],
                "consumed_by": ["p", "w", "a", "pi"],
            },
            "visibility": {
                "preset_mode": "hidden",
                "mechanism_layer": True,
                "operator_layer": True,
                "expert_mode": True,
                "results_overlay": False,
            },
        },
        "prediction": {
            "id": "prediction",
            "label": "Prediction",
            "group": "prediction",
            "pedagogy": {
                "intuition": "What the model expects before feedback arrives.",
                "mechanism": "Outcome estimate from current state and parameters.",
                "operator_view": "Field written by prediction operators and read by error/policy stages.",
                "expert": "Scalar in simple presets, vector in richer models.",
            },
            "runtime": {
                "kind": "float",
                "shape": "scalar_or_vector",
                "nullable": False,
                "default": 0.0,
                "produced_by": ["p"],
                "consumed_by": ["delta", "pi", "m"],
            },
            "visibility": {
                "preset_mode": "hidden",
                "mechanism_layer": True,
                "operator_layer": True,
                "expert_mode": True,
                "results_overlay": True,
            },
        },
        "outcome": {
            "id": "outcome",
            "label": "Outcome",
            "group": "outcome",
            "pedagogy": {
                "intuition": "What actually happened on the trial.",
                "mechanism": "Observed reinforcement or feedback used for learning signals.",
                "operator_view": "Feedback field read by discrepancy operators.",
                "expert": "Can be scalar or structured feedback.",
            },
            "runtime": {
                "kind": "float",
                "shape": "scalar_or_vector",
                "nullable": False,
                "default": 0.0,
                "produced_by": ["env"],
                "consumed_by": ["delta", "m"],
            },
            "visibility": {
                "preset_mode": "hidden",
                "mechanism_layer": True,
                "operator_layer": True,
                "expert_mode": True,
                "results_overlay": True,
            },
        },
        "error": {
            "id": "error",
            "label": "Prediction Error",
            "group": "learning_signal",
            "pedagogy": {
                "intuition": "How wrong the model was on this trial.",
                "mechanism": "Mismatch between predicted and observed outcomes.",
                "operator_view": "Discrepancy field consumed by update and attention stages.",
                "expert": "Can be classical PE, TD error, or another teaching signal.",
            },
            "runtime": {
                "kind": "float",
                "shape": "scalar_or_vector",
                "nullable": False,
                "default": 0.0,
                "produced_by": ["delta"],
                "consumed_by": ["w", "a", "e", "m"],
            },
            "visibility": {
                "preset_mode": "hidden",
                "mechanism_layer": True,
                "operator_layer": True,
                "expert_mode": True,
                "results_overlay": True,
            },
        },
        "weights": {
            "id": "weights",
            "label": "Associative Strength / Weights",
            "group": "update_state",
            "pedagogy": {
                "intuition": "Learned strength of cue-outcome relationships.",
                "mechanism": "Parameters that determine future predictions.",
                "operator_view": "Persistent field read by prediction and written by update operators.",
                "expert": "Scalar, vector, or matrix depending on learner/representation.",
            },
            "runtime": {
                "kind": "array",
                "shape": "scalar_or_vector_or_matrix",
                "nullable": False,
                "default": [],
                "produced_by": ["w"],
                "consumed_by": ["p", "m"],
            },
            "visibility": {
                "preset_mode": "hidden",
                "mechanism_layer": False,
                "operator_layer": True,
                "expert_mode": True,
                "results_overlay": True,
            },
        },
        "weight_delta": {
            "id": "weight_delta",
            "label": "Update Effect",
            "group": "update_state",
            "pedagogy": {
                "intuition": "How much learning changed on this trial.",
                "mechanism": "Parameter increment produced by update rules.",
                "operator_view": "Transient update term derived from error and learning rate.",
                "expert": "Useful as an explainability overlay.",
            },
            "runtime": {
                "kind": "float",
                "shape": "scalar_or_vector",
                "nullable": True,
                "default": None,
                "produced_by": ["w"],
                "consumed_by": ["m"],
            },
            "visibility": {
                "preset_mode": "hidden",
                "mechanism_layer": False,
                "operator_layer": True,
                "expert_mode": True,
                "results_overlay": True,
            },
        },
        "associability": {
            "id": "associability",
            "label": "Associability",
            "group": "attention_memory",
            "pedagogy": {
                "intuition": "How learnable a cue currently is.",
                "mechanism": "Dynamic sensitivity factor that modulates update strength.",
                "operator_view": "Field written by attention operators and consumed by update stages.",
                "expert": "Can reflect different attention-model semantics.",
            },
            "runtime": {
                "kind": "float",
                "shape": "scalar_or_vector",
                "nullable": True,
                "default": None,
                "produced_by": ["a"],
                "consumed_by": ["w", "m"],
            },
            "visibility": {
                "preset_mode": "hidden",
                "mechanism_layer": False,
                "operator_layer": True,
                "expert_mode": True,
                "results_overlay": True,
            },
        },
        "selected_action": {
            "id": "selected_action",
            "label": "Selected Action",
            "group": "action_policy",
            "pedagogy": {
                "intuition": "Action taken on this trial.",
                "mechanism": "Sampled or chosen behavior produced by policy stage.",
                "operator_view": "Action field consumed by environment and evaluation stages.",
                "expert": "Primarily relevant for operant presets.",
            },
            "runtime": {
                "kind": "string",
                "shape": "scalar",
                "nullable": True,
                "default": None,
                "produced_by": ["pi"],
                "consumed_by": ["env", "m"],
            },
            "visibility": {
                "preset_mode": "hidden",
                "mechanism_layer": True,
                "operator_layer": True,
                "expert_mode": True,
                "results_overlay": True,
            },
        },
        "response_strength": {
            "id": "response_strength",
            "label": "Response Strength",
            "group": "evaluation",
            "pedagogy": {
                "intuition": "How strongly the model responds.",
                "mechanism": "Derived output for reports and plots.",
                "operator_view": "Evaluation-layer readout from internal state/action variables.",
                "expert": "May be computed instead of persisted.",
            },
            "runtime": {
                "kind": "float",
                "shape": "scalar",
                "nullable": True,
                "default": None,
                "produced_by": ["m"],
                "consumed_by": [],
            },
            "visibility": {
                "preset_mode": "hidden",
                "mechanism_layer": False,
                "operator_layer": False,
                "expert_mode": True,
                "results_overlay": True,
            },
        },
        "trial_index": {
            "id": "trial_index",
            "label": "Trial Index",
            "group": "metadata",
            "pedagogy": {
                "intuition": "Which trial this is in sequence.",
                "mechanism": "Bookkeeping value for ordering and overlays.",
                "operator_view": "Metadata field not modified by core learning operators.",
                "expert": "Useful for debug joins and per-trial overlays.",
            },
            "runtime": {
                "kind": "integer",
                "shape": "scalar",
                "nullable": False,
                "default": 0,
                "produced_by": [],
                "consumed_by": ["m"],
            },
            "visibility": {
                "preset_mode": "hidden",
                "mechanism_layer": False,
                "operator_layer": False,
                "expert_mode": True,
                "results_overlay": True,
            },
        },
        "phase_name": {
            "id": "phase_name",
            "label": "Phase Name",
            "group": "metadata",
            "pedagogy": {
                "intuition": "The phase containing this trial.",
                "mechanism": "Protocol label for segmentation and plotting.",
                "operator_view": "Metadata for phase-aware interpretation.",
                "expert": "Used for phase boundaries in graphs.",
            },
            "runtime": {
                "kind": "string",
                "shape": "scalar",
                "nullable": False,
                "default": "",
                "produced_by": [],
                "consumed_by": ["m"],
            },
            "visibility": {
                "preset_mode": "hidden",
                "mechanism_layer": True,
                "operator_layer": False,
                "expert_mode": True,
                "results_overlay": True,
            },
        },
    },
}


_REQUIRED_TOP_LEVEL_KEYS: tuple[str, ...] = (
    "version",
    "field_groups",
    "visibility_policies",
    "fields",
)
_REQUIRED_FIELD_KEYS: tuple[str, ...] = (
    "id",
    "label",
    "group",
    "pedagogy",
    "runtime",
    "visibility",
)
_REQUIRED_PEDAGOGY_KEYS: tuple[str, ...] = (
    "intuition",
    "mechanism",
    "operator_view",
    "expert",
)
_REQUIRED_RUNTIME_KEYS: tuple[str, ...] = (
    "kind",
    "shape",
    "nullable",
    "default",
    "produced_by",
    "consumed_by",
)
_REQUIRED_VISIBILITY_KEYS: tuple[str, ...] = (
    "preset_mode",
    "mechanism_layer",
    "operator_layer",
    "expert_mode",
    "results_overlay",
)


def _require_dict(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise TrialStateRegistryValidationError(f"{label} must be an object.")
    return value


def _require_non_empty_string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise TrialStateRegistryValidationError(f"{label} must be a non-empty string.")
    return value


def _require_bool(value: Any, label: str) -> None:
    if not isinstance(value, bool):
        raise TrialStateRegistryValidationError(f"{label} must be boolean.")


def _require_string_list(value: Any, label: str) -> list[str]:
    if not isinstance(value, list):
        raise TrialStateRegistryValidationError(f"{label} must be a list of strings.")
    out: list[str] = []
    for idx, item in enumerate(value):
        out.append(_require_non_empty_string(item, f"{label}[{idx}]"))
    return out


def validate_trialstate_field_registry(registry: dict[str, Any] | None = None) -> dict[str, Any]:
    """Validate registry contract shape and invariants; return normalized deep copy."""
    payload = deepcopy(TRIALSTATE_FIELD_REGISTRY if registry is None else registry)
    root = _require_dict(payload, "trialstate_registry")

    for key in _REQUIRED_TOP_LEVEL_KEYS:
        if key not in root:
            raise TrialStateRegistryValidationError(f"trialstate_registry missing required key: {key}")

    _require_non_empty_string(root.get("version"), "trialstate_registry.version")
    groups = _require_dict(root.get("field_groups"), "trialstate_registry.field_groups")
    _require_dict(root.get("visibility_policies"), "trialstate_registry.visibility_policies")
    fields = _require_dict(root.get("fields"), "trialstate_registry.fields")

    for group in REQUIRED_TRIALSTATE_FIELD_GROUPS:
        if group not in groups:
            raise TrialStateRegistryValidationError(
                f"trialstate_registry.field_groups missing required group: {group}"
            )
        group_payload = _require_dict(groups[group], f"trialstate_registry.field_groups.{group}")
        _require_non_empty_string(group_payload.get("label"), f"trialstate_registry.field_groups.{group}.label")
        _require_non_empty_string(
            group_payload.get("description"), f"trialstate_registry.field_groups.{group}.description"
        )

    seen_ids: set[str] = set()
    for field_key, raw_field in fields.items():
        field = _require_dict(raw_field, f"trialstate_registry.fields.{field_key}")
        for key in _REQUIRED_FIELD_KEYS:
            if key not in field:
                raise TrialStateRegistryValidationError(
                    f"trialstate_registry.fields.{field_key} missing required key: {key}"
                )
        field_id = _require_non_empty_string(field.get("id"), f"trialstate_registry.fields.{field_key}.id")
        if field_id in seen_ids:
            raise TrialStateRegistryValidationError(
                f"trialstate_registry.fields has duplicate id value: {field_id}"
            )
        seen_ids.add(field_id)
        if field_id != field_key:
            raise TrialStateRegistryValidationError(
                f"trialstate_registry.fields.{field_key}.id must match field key '{field_key}'."
            )

        _require_non_empty_string(field.get("label"), f"trialstate_registry.fields.{field_key}.label")
        group = _require_non_empty_string(field.get("group"), f"trialstate_registry.fields.{field_key}.group")
        if group not in groups:
            raise TrialStateRegistryValidationError(
                f"trialstate_registry.fields.{field_key}.group references unknown group: {group}"
            )

        pedagogy = _require_dict(field.get("pedagogy"), f"trialstate_registry.fields.{field_key}.pedagogy")
        for key in _REQUIRED_PEDAGOGY_KEYS:
            _require_non_empty_string(pedagogy.get(key), f"trialstate_registry.fields.{field_key}.pedagogy.{key}")

        runtime = _require_dict(field.get("runtime"), f"trialstate_registry.fields.{field_key}.runtime")
        for key in _REQUIRED_RUNTIME_KEYS:
            if key not in runtime:
                raise TrialStateRegistryValidationError(
                    f"trialstate_registry.fields.{field_key}.runtime missing required key: {key}"
                )
        _require_non_empty_string(runtime.get("kind"), f"trialstate_registry.fields.{field_key}.runtime.kind")
        _require_non_empty_string(runtime.get("shape"), f"trialstate_registry.fields.{field_key}.runtime.shape")
        _require_bool(runtime.get("nullable"), f"trialstate_registry.fields.{field_key}.runtime.nullable")
        _require_string_list(
            runtime.get("produced_by"), f"trialstate_registry.fields.{field_key}.runtime.produced_by"
        )
        _require_string_list(
            runtime.get("consumed_by"), f"trialstate_registry.fields.{field_key}.runtime.consumed_by"
        )

        visibility = _require_dict(field.get("visibility"), f"trialstate_registry.fields.{field_key}.visibility")
        for key in _REQUIRED_VISIBILITY_KEYS:
            if key not in visibility:
                raise TrialStateRegistryValidationError(
                    f"trialstate_registry.fields.{field_key}.visibility missing required key: {key}"
                )
        _require_non_empty_string(
            visibility.get("preset_mode"), f"trialstate_registry.fields.{field_key}.visibility.preset_mode"
        )
        _require_bool(
            visibility.get("mechanism_layer"),
            f"trialstate_registry.fields.{field_key}.visibility.mechanism_layer",
        )
        _require_bool(
            visibility.get("operator_layer"),
            f"trialstate_registry.fields.{field_key}.visibility.operator_layer",
        )
        _require_bool(
            visibility.get("expert_mode"),
            f"trialstate_registry.fields.{field_key}.visibility.expert_mode",
        )
        _require_bool(
            visibility.get("results_overlay"),
            f"trialstate_registry.fields.{field_key}.visibility.results_overlay",
        )

    for field_name in REQUIRED_TRIALSTATE_FIELDS:
        if field_name not in fields:
            raise TrialStateRegistryValidationError(
                f"trialstate_registry.fields missing required baseline field: {field_name}"
            )

    return payload


def get_trialstate_field_registry() -> dict[str, Any]:
    """Return validated deep-copied TrialState field registry."""
    return validate_trialstate_field_registry(TRIALSTATE_FIELD_REGISTRY)


def list_trialstate_field_ids() -> tuple[str, ...]:
    """Return stable sorted field IDs from the canonical registry."""
    payload = get_trialstate_field_registry()
    return tuple(sorted(payload["fields"].keys()))


def get_trialstate_field(field_id: str) -> dict[str, Any]:
    """Resolve a single field contract by field ID."""
    key = _require_non_empty_string(field_id, "field_id")
    payload = get_trialstate_field_registry()
    fields = payload["fields"]
    if key not in fields:
        available = ", ".join(sorted(fields.keys()))
        raise KeyError(f"Unknown TrialState field '{key}'. Available fields: {available}")
    return deepcopy(fields[key])
