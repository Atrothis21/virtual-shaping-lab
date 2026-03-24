"""Declarative agent-bundle registry contract for arrangement x task composition."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from ui.contracts.arrangement_contract import list_arrangement_ids
from ui.contracts.operator_basis_registry import (
    get_internal_builder_family,
    list_ui_selectable_implementations,
)


class AgentBundleRegistryValidationError(ValueError):
    """Raised when agent bundle registry contract validation fails."""


AGENT_BUNDLE_REGISTRY_VERSION = "3.15.0"
_ALLOWED_SELECTION_SLOTS: tuple[str, ...] = (
    "phi",
    "c",
    "g",
    "e",
    "p",
    "delta",
    "a",
    "w",
    "pi",
    "omega",
    "m",
)
_ALLOWED_BUILDER_FAMILIES: tuple[str, ...] = (
    "representation",
    "learner",
    "agent_control",
    "environment_protocol",
    "report_readout",
)
_PRIMARY_DECLARATIVE_IDENTITY_POLICY = (
    "Agent bundle identity is defined by declarative operator selections; "
    "builder-family constraints are secondary metadata only."
)

AGENT_BUNDLE_REGISTRY: dict[str, Any] = {
    "version": AGENT_BUNDLE_REGISTRY_VERSION,
    "primary_identity_policy": _PRIMARY_DECLARATIVE_IDENTITY_POLICY,
    "bundles": {
        "rw_classical": {
            "id": "rw_classical",
            "label": "RW Classical Bundle",
            "description": "Classical RW-style bundle for pavlovian acquisition/extinction families.",
            "arrangement_compatibility": ["pavlovian"],
            "operator_selections": {
                "phi": "elemental",
                "p": "state_value",
                "delta": "rw_error",
                "a": "fixed_alpha",
                "w": "rescorla_wagner",
                "omega": "classical_contingency",
                "m": ["trial_log", "learning_curve", "report_bundle"],
            },
            "builder_family_constraints": {
                "representation": {"allowed": ["representation"]},
                "learner": {"allowed": ["learner"]},
                "environment_protocol": {"allowed": ["environment_protocol"]},
                "report_readout": {"allowed": ["report_readout"]},
            },
            "selectable_universe_source": "operator_basis_registry",
        },
        "rw_operant": {
            "id": "rw_operant",
            "label": "RW Operant Bundle",
            "description": "RW-style action-capable bundle for operant arrangements.",
            "arrangement_compatibility": ["operant"],
            "operator_selections": {
                "phi": "elemental",
                "p": "action_value",
                "delta": "reward_prediction_error",
                "a": "fixed_alpha",
                "w": "rescorla_wagner",
                "pi": "epsilon_greedy",
                "omega": "operant_contingency",
                "m": ["trial_log", "action_probabilities", "report_bundle"],
            },
            "builder_family_constraints": {
                "representation": {"allowed": ["representation"]},
                "learner": {"allowed": ["learner"]},
                "agent_control": {"allowed": ["agent_control"]},
                "environment_protocol": {"allowed": ["environment_protocol"]},
                "report_readout": {"allowed": ["report_readout"]},
            },
            "selectable_universe_source": "operator_basis_registry",
        },
        "legacy_hybrid_bundle": {
            "id": "legacy_hybrid_bundle",
            "label": "Legacy Hybrid Bundle",
            "description": "Hybrid bridge bundle retained only for policy-level forbidden tuple checks.",
            "arrangement_compatibility": ["hybrid"],
            "operator_selections": {
                "phi": "hybrid_elemental_configural",
                "p": "state_action_value",
                "delta": "advantage_error",
                "w": "actor_critic_update",
                "pi": "softmax",
                "omega": "contextual_contingency",
                "m": ["trial_log", "report_bundle"],
            },
            "builder_family_constraints": {
                "representation": {"allowed": ["representation"]},
                "learner": {"allowed": ["learner"]},
                "agent_control": {"allowed": ["agent_control"]},
                "environment_protocol": {"allowed": ["environment_protocol"]},
                "report_readout": {"allowed": ["report_readout"]},
            },
            "selectable_universe_source": "operator_basis_registry",
        },
    },
}


def _require_dict(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise AgentBundleRegistryValidationError(f"{label} must be an object.")
    return value


def _require_non_empty_string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise AgentBundleRegistryValidationError(f"{label} must be a non-empty string.")
    return value


def _require_string_list(value: Any, label: str) -> list[str]:
    if not isinstance(value, list):
        raise AgentBundleRegistryValidationError(f"{label} must be a list of strings.")
    out: list[str] = []
    seen: set[str] = set()
    for idx, item in enumerate(value):
        key = _require_non_empty_string(item, f"{label}[{idx}]")
        if key in seen:
            raise AgentBundleRegistryValidationError(f"{label} has duplicate value: {key}")
        seen.add(key)
        out.append(key)
    return out


def _validate_operator_selections(bundle_id: str, operator_selections: dict[str, Any]) -> None:
    known_slots = set(_ALLOWED_SELECTION_SLOTS)
    unknown_slots = sorted(set(operator_selections.keys()) - known_slots)
    if unknown_slots:
        raise AgentBundleRegistryValidationError(
            f"agent_bundle_registry.bundles.{bundle_id}.operator_selections has unknown slots: {', '.join(unknown_slots)}"
        )
    required = {"phi", "p", "delta", "w", "omega", "m"}
    missing_required = sorted(required - set(operator_selections.keys()))
    if missing_required:
        raise AgentBundleRegistryValidationError(
            "agent_bundle_registry.bundles."
            f"{bundle_id}.operator_selections missing required slots: {', '.join(missing_required)}"
        )

    for slot, selection in operator_selections.items():
        allowed = set(list_ui_selectable_implementations(slot))
        if slot == "m":
            values = _require_string_list(
                selection,
                f"agent_bundle_registry.bundles.{bundle_id}.operator_selections.{slot}",
            )
            for value in values:
                if value not in allowed:
                    raise AgentBundleRegistryValidationError(
                        "agent_bundle_registry.bundles."
                        f"{bundle_id}.operator_selections.{slot} has unknown selection: {value}"
                    )
        else:
            value = _require_non_empty_string(
                selection,
                f"agent_bundle_registry.bundles.{bundle_id}.operator_selections.{slot}",
            )
            if value not in allowed:
                raise AgentBundleRegistryValidationError(
                    "agent_bundle_registry.bundles."
                    f"{bundle_id}.operator_selections.{slot} has unknown selection: {value}"
                )


def _validate_builder_family_constraints(bundle_id: str, bundle: dict[str, Any]) -> None:
    constraints = _require_dict(
        bundle.get("builder_family_constraints"),
        f"agent_bundle_registry.bundles.{bundle_id}.builder_family_constraints",
    )
    for family, raw in constraints.items():
        fam = _require_non_empty_string(
            family,
            f"agent_bundle_registry.bundles.{bundle_id}.builder_family_constraints.family",
        )
        if fam not in set(_ALLOWED_BUILDER_FAMILIES):
            raise AgentBundleRegistryValidationError(
                f"agent_bundle_registry.bundles.{bundle_id}.builder_family_constraints has unknown family: {fam}"
            )
        payload = _require_dict(
            raw,
            f"agent_bundle_registry.bundles.{bundle_id}.builder_family_constraints.{family}",
        )
        for key in ("allowed",):
            if key not in payload:
                raise AgentBundleRegistryValidationError(
                    "agent_bundle_registry.bundles."
                    f"{bundle_id}.builder_family_constraints.{family} missing required key: {key}"
                )
        allowed = _require_string_list(
            payload.get("allowed"),
            f"agent_bundle_registry.bundles.{bundle_id}.builder_family_constraints.{family}.allowed",
        )
        for name in allowed:
            if name not in set(_ALLOWED_BUILDER_FAMILIES):
                raise AgentBundleRegistryValidationError(
                    "agent_bundle_registry.bundles."
                    f"{bundle_id}.builder_family_constraints.{family}.allowed has unknown family: {name}"
                )

    selections = _require_dict(
        bundle.get("operator_selections"),
        f"agent_bundle_registry.bundles.{bundle_id}.operator_selections",
    )
    # Secondary metadata check: constraints cannot contradict family routing implied by selections.
    for slot, value in selections.items():
        if slot == "m":
            choices = _require_string_list(
                value,
                f"agent_bundle_registry.bundles.{bundle_id}.operator_selections.{slot}",
            )
        else:
            choices = [
                _require_non_empty_string(
                    value,
                    f"agent_bundle_registry.bundles.{bundle_id}.operator_selections.{slot}",
                )
            ]
        for selection in choices:
            family = get_internal_builder_family(slot, selection)
            if family in constraints:
                allowed = constraints[family]["allowed"]
                if family not in allowed:
                    raise AgentBundleRegistryValidationError(
                        "agent_bundle_registry.bundles."
                        f"{bundle_id}.builder_family_constraints.{family} contradicts routed family '{family}'."
                    )


def validate_agent_bundle_registry(registry: dict[str, Any] | None = None) -> dict[str, Any]:
    """Validate agent bundle registry contract and return deep copy."""
    payload = deepcopy(AGENT_BUNDLE_REGISTRY if registry is None else registry)
    root = _require_dict(payload, "agent_bundle_registry")
    for key in ("version", "primary_identity_policy", "bundles"):
        if key not in root:
            raise AgentBundleRegistryValidationError(
                f"agent_bundle_registry missing required key: {key}"
            )
    _require_non_empty_string(root.get("version"), "agent_bundle_registry.version")
    identity_policy = _require_non_empty_string(
        root.get("primary_identity_policy"),
        "agent_bundle_registry.primary_identity_policy",
    )
    if "declarative operator selections" not in identity_policy.lower():
        raise AgentBundleRegistryValidationError(
            "agent_bundle_registry.primary_identity_policy must explicitly anchor declarative identity."
        )

    bundles = _require_dict(root.get("bundles"), "agent_bundle_registry.bundles")
    known_arrangements = set(list_arrangement_ids()) | {"hybrid"}
    for bundle_key, raw in bundles.items():
        bundle = _require_dict(raw, f"agent_bundle_registry.bundles.{bundle_key}")
        for key in (
            "id",
            "label",
            "description",
            "arrangement_compatibility",
            "operator_selections",
            "builder_family_constraints",
            "selectable_universe_source",
        ):
            if key not in bundle:
                raise AgentBundleRegistryValidationError(
                    f"agent_bundle_registry.bundles.{bundle_key} missing required key: {key}"
                )
        bundle_id = _require_non_empty_string(
            bundle.get("id"),
            f"agent_bundle_registry.bundles.{bundle_key}.id",
        )
        if bundle_id != bundle_key:
            raise AgentBundleRegistryValidationError(
                f"agent_bundle_registry.bundles.{bundle_key}.id must match bundle key '{bundle_key}'."
            )
        _require_non_empty_string(
            bundle.get("label"),
            f"agent_bundle_registry.bundles.{bundle_key}.label",
        )
        _require_non_empty_string(
            bundle.get("description"),
            f"agent_bundle_registry.bundles.{bundle_key}.description",
        )
        arrangements = _require_string_list(
            bundle.get("arrangement_compatibility"),
            f"agent_bundle_registry.bundles.{bundle_key}.arrangement_compatibility",
        )
        for arrangement_id in arrangements:
            if arrangement_id not in known_arrangements:
                raise AgentBundleRegistryValidationError(
                    "agent_bundle_registry.bundles."
                    f"{bundle_key}.arrangement_compatibility has unknown arrangement: {arrangement_id}"
                )
        source = _require_non_empty_string(
            bundle.get("selectable_universe_source"),
            f"agent_bundle_registry.bundles.{bundle_key}.selectable_universe_source",
        )
        if source != "operator_basis_registry":
            raise AgentBundleRegistryValidationError(
                f"agent_bundle_registry.bundles.{bundle_key}.selectable_universe_source must be 'operator_basis_registry'."
            )

        selections = _require_dict(
            bundle.get("operator_selections"),
            f"agent_bundle_registry.bundles.{bundle_key}.operator_selections",
        )
        _validate_operator_selections(bundle_key, selections)
        _validate_builder_family_constraints(bundle_key, bundle)

    return payload


def get_agent_bundle_registry() -> dict[str, Any]:
    """Return validated agent bundle registry payload."""
    return validate_agent_bundle_registry(AGENT_BUNDLE_REGISTRY)


def list_agent_bundle_ids() -> tuple[str, ...]:
    """Return stable bundle ID ordering."""
    payload = get_agent_bundle_registry()
    return tuple(sorted(payload["bundles"].keys()))


def get_agent_bundle(bundle_id: str) -> dict[str, Any]:
    """Return one agent bundle."""
    key = _require_non_empty_string(bundle_id, "bundle_id")
    payload = get_agent_bundle_registry()
    bundles = payload["bundles"]
    if key not in bundles:
        known = ", ".join(sorted(bundles.keys()))
        raise AgentBundleRegistryValidationError(
            f"Unknown agent bundle id '{key}'. Known IDs: {known}"
        )
    return deepcopy(bundles[key])


def validate_agent_bundle_arrangement_compatibility(
    *,
    bundle_id: str,
    arrangement_id: str,
) -> dict[str, Any]:
    """Validate arrangement compatibility for bundle."""
    bundle = get_agent_bundle(bundle_id)
    arrangement = _require_non_empty_string(arrangement_id, "arrangement_id")
    supported = set(bundle["arrangement_compatibility"])
    if arrangement not in supported:
        raise AgentBundleRegistryValidationError(
            f"agent bundle '{bundle_id}' is not compatible with arrangement '{arrangement}'."
        )
    return bundle

