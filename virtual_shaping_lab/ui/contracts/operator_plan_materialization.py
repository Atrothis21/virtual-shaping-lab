"""Materialize compiled operator-basis specs into canonical plan payload sections."""

from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from typing import Any

from ui.contracts.operator_selection_compiler import (
    compile_operator_selection_artifact,
)


OPERATOR_PLAN_MATERIALIZATION_VERSION = "3.12.5"


class OperatorPlanMaterializationError(ValueError):
    """Raised when compiled basis cannot be materialized into canonical payload sections."""


_SUPPORTED_PROTOCOL_FAMILIES: tuple[str, ...] = (
    "acquisition",
    "extinction",
    "differential_acquisition",
)

_REPRESENTATION_NAME_MAP: dict[str, str] = {
    "elemental": "vector_elemental",
    "compound_elemental": "vector_elemental",
    "binary_feature_vector": "vector_elemental",
    "dense_feature_vector": "vector_hybrid",
    "configural": "vector_hybrid",
    "hybrid_elemental_configural": "vector_hybrid",
    "identity": "vector_elemental",
    "temporal_stub": "vector_hybrid",
}

_LEARNING_RULE_MAP: dict[str, str] = {
    "rescorla_wagner": "rescorla_wagner",
    "delta_rule": "rescorla_wagner",
    "td0_update": "temporal_difference",
    "td_lambda_update": "temporal_difference",
    "q_learning_update": "q_learner",
    "sarsa_update": "q_learner",
    "actor_critic_update": "q_learner",
    "linear_gradient_update": "rescorla_wagner",
    "criterion_shift_update": "rescorla_wagner",
}


def _stable_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"))


def _stable_hash(payload: dict[str, Any]) -> str:
    return hashlib.sha256(_stable_json(payload).encode("utf-8")).hexdigest()


def _selection(slot_payload: dict[str, Any]) -> str | None:
    values = slot_payload.get("effective_selection_ids", [])
    if not isinstance(values, list) or not values:
        return None
    return str(values[0])


def _selection_list(slot_payload: dict[str, Any]) -> list[str]:
    values = slot_payload.get("effective_selection_ids", [])
    if not isinstance(values, list):
        return []
    return [str(v) for v in values]


def _require_compiled_artifact(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise OperatorPlanMaterializationError("compiled artifact must be an object.")
    if "normalized_slots" not in payload or "assembly_spec" not in payload:
        raise OperatorPlanMaterializationError(
            "compiled artifact missing required keys: normalized_slots, assembly_spec"
        )
    normalized_slots = payload.get("normalized_slots")
    if not isinstance(normalized_slots, dict):
        raise OperatorPlanMaterializationError("compiled artifact.normalized_slots must be an object.")
    return payload


def _protocol_template(protocol_family: str, *, stimuli_catalog: list[str]) -> list[dict[str, Any]]:
    if protocol_family == "acquisition":
        return [
            {
                "name": "Acquisition",
                "protocol": "acquisition",
                "stimuli": {"cs_plus": [stimuli_catalog[0]]},
                "params": {"n_trials": 100},
                "trials": 100,
            }
        ]
    if protocol_family == "extinction":
        return [
            {
                "name": "Extinction",
                "protocol": "extinction",
                "stimuli": {"cs_plus": [stimuli_catalog[0]]},
                "params": {
                    "n_acquisition_trials": 50,
                    "n_extinction_trials": 50,
                },
                "trials": 100,
            }
        ]
    if protocol_family == "differential_acquisition":
        cs_minus = stimuli_catalog[1] if len(stimuli_catalog) > 1 else "noise"
        return [
            {
                "name": "Differential Acquisition",
                "protocol": "differential_acquisition",
                "stimuli": {"cs_plus": [stimuli_catalog[0]], "cs_minus": [cs_minus]},
                "params": {"n_trials": 100},
                "trials": 100,
            }
        ]
    raise OperatorPlanMaterializationError(
        f"Unsupported protocol_family '{protocol_family}'. "
        f"Supported families: {', '.join(_SUPPORTED_PROTOCOL_FAMILIES)}"
    )


def _build_route_map(compiled_artifact: dict[str, Any]) -> dict[str, list[dict[str, str]]]:
    assembly_slots = compiled_artifact["assembly_spec"]["slots"]
    route_map: dict[str, list[dict[str, str]]] = {}
    for slot, slot_payload in sorted(assembly_slots.items()):
        selection_ids = slot_payload.get("selection_ids", [])
        families = slot_payload.get("internal_builder_families", [])
        entries: list[dict[str, str]] = []
        for idx, selection_id in enumerate(selection_ids):
            entries.append(
                {
                    "selection_id": str(selection_id),
                    "internal_builder_family": str(families[idx]),
                }
            )
        route_map[slot] = entries
    return route_map


def materialize_compiled_operator_plan_sections(
    compiled_artifact: dict[str, Any],
    *,
    protocol_family: str = "acquisition",
    stimuli_catalog: list[str] | None = None,
) -> dict[str, Any]:
    """Map compiled selection artifact into canonical experiment payload sections."""
    compiled = _require_compiled_artifact(deepcopy(compiled_artifact))
    if protocol_family not in _SUPPORTED_PROTOCOL_FAMILIES:
        raise OperatorPlanMaterializationError(
            f"Unsupported protocol_family '{protocol_family}'."
        )
    catalog = list(stimuli_catalog or ["tone", "noise"])
    if not catalog:
        raise OperatorPlanMaterializationError("stimuli_catalog must contain at least one stimulus.")

    slots = compiled["normalized_slots"]
    phi = _selection(slots["phi"]) or "elemental"
    p = _selection(slots["p"]) or "state_value"
    delta = _selection(slots["delta"]) or "rw_error"
    a = _selection(slots["a"]) or "none"
    e = _selection(slots["e"]) or "none"
    g = _selection(slots["g"]) or "none"
    w = _selection(slots["w"]) or "rescorla_wagner"
    pi = _selection(slots["pi"])
    omega = _selection(slots["omega"]) or "classical_contingency"
    m = _selection_list(slots["m"])

    representation_name = _REPRESENTATION_NAME_MAP.get(phi, "vector_elemental")
    learning_rule = _LEARNING_RULE_MAP.get(w, w)
    route_map = _build_route_map(compiled)

    phases = _protocol_template(protocol_family, stimuli_catalog=catalog)
    for phase in phases:
        phase["operator_attachments"] = {
            "environment_operator": omega,
            "measurement_outputs": list(m),
            "route_map": deepcopy(route_map),
        }

    payload = {
        "experiment": {
            "agent": {
                "name": "classical_agent",
                "representation": {
                    "name": representation_name,
                    "params": {"stimuli": list(catalog), "max_compound_size": 2},
                },
                "learning": {
                    "rule": learning_rule,
                    "params": {
                        "prediction_operator": p,
                        "error_operator": delta,
                        "attention_operator": a,
                        "eligibility_operator": e,
                        "generalization_operator": g,
                        "update_operator": w,
                    },
                },
                "policy": None if pi in {None, "none"} else {"name": pi, "params": {}},
            },
            "runtime": {
                "environment": {"name": omega, "params": {}},
                "measurement": {"outputs": list(m)},
                "operator_routes": deepcopy(route_map),
            },
            "program": {"phases": phases},
        }
    }
    return payload


def compile_and_materialize_operator_plan(
    preset_definition: dict[str, Any],
    *,
    protocol_family: str = "acquisition",
    stimuli_catalog: list[str] | None = None,
) -> dict[str, Any]:
    """Compile subset contract and materialize canonical plan payload sections."""
    compiled = compile_operator_selection_artifact(preset_definition)
    payload = materialize_compiled_operator_plan_sections(
        compiled,
        protocol_family=protocol_family,
        stimuli_catalog=stimuli_catalog,
    )
    payload["materialization"] = {
        "version": OPERATOR_PLAN_MATERIALIZATION_VERSION,
        "protocol_family": protocol_family,
        "compiled_hash": compiled["frozen_compiled_hash"],
    }
    payload["materialization"]["materialized_hash"] = _stable_hash(payload)
    return payload


def stable_materialized_operator_plan_json(payload: dict[str, Any]) -> str:
    """Deterministic JSON for materialized operator plan payload."""
    return _stable_json(payload)


def stable_materialized_operator_plan_hash(payload: dict[str, Any]) -> str:
    """Deterministic hash for materialized operator plan payload."""
    return _stable_hash(payload)

