"""Basis-driven builder-family routing contract for assembly cutover."""

from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from typing import Any

from experiment.domain.types import ExperimentPlan


class BasisAssemblyRoutingError(ValueError):
    """Raised when basis routing artifact is invalid or inconsistent."""


BASIS_ASSEMBLY_ROUTING_VERSION = "3.13.0"

SLOT_TO_BUILDER_FAMILY: dict[str, str] = {
    "phi": "representation",
    "c": "representation",
    "g": "representation",
    "e": "learner",
    "p": "learner",
    "delta": "learner",
    "a": "learner",
    "w": "learner",
    "pi": "agent_control",
    "omega": "environment_protocol",
    "m": "report_readout",
}

FAMILY_GROUPS: dict[str, tuple[str, ...]] = {
    "representation_family": ("phi", "c", "g"),
    "learner_family": ("e", "p", "delta", "a", "w"),
    "agent_control_family": ("pi",),
    "environment_protocol_family": ("omega",),
    "report_readout_family": ("m",),
}

_SLOT_TO_GROUP: dict[str, str] = {
    slot: group for group, slots in FAMILY_GROUPS.items() for slot in slots
}


def _stable_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"))


def _stable_hash(payload: dict[str, Any]) -> str:
    return hashlib.sha256(_stable_json(payload).encode("utf-8")).hexdigest()


def _load_route_payloads(plan: ExperimentPlan) -> dict[str, Any]:
    basis_compile = dict(plan.basis_compile_artifact or {})
    if isinstance(basis_compile.get("assembly_spec"), dict):
        slots = basis_compile["assembly_spec"].get("slots", {})
        if isinstance(slots, dict):
            out: dict[str, Any] = {}
            for slot, payload in slots.items():
                selection_ids = payload.get("selection_ids", [])
                families = payload.get("internal_builder_families", [])
                out[slot] = {"selection_ids": selection_ids, "internal_builder_families": families}
            return out

    materialized = dict(plan.basis_materialized_sections or {})
    experiment = materialized.get("experiment", {}) if isinstance(materialized.get("experiment"), dict) else {}
    runtime = experiment.get("runtime", {}) if isinstance(experiment.get("runtime"), dict) else {}
    routes = runtime.get("operator_routes")
    if isinstance(routes, dict):
        out: dict[str, Any] = {}
        for slot, entries in routes.items():
            if not isinstance(entries, list):
                continue
            selection_ids: list[str] = []
            families: list[str] = []
            for entry in entries:
                if not isinstance(entry, dict):
                    continue
                selection_ids.append(str(entry.get("selection_id", "")))
                families.append(str(entry.get("internal_builder_family", "")))
            out[slot] = {"selection_ids": selection_ids, "internal_builder_families": families}
        return out
    return {}


def build_basis_assembly_routing_contract(plan: ExperimentPlan) -> dict[str, Any]:
    """Build validated routing contract from plan basis compile/materialized references."""
    if not isinstance(plan, ExperimentPlan):
        raise BasisAssemblyRoutingError("plan must be an ExperimentPlan.")
    route_payloads = _load_route_payloads(plan)
    if not route_payloads:
        raise BasisAssemblyRoutingError(
            "Plan does not contain basis routing references in basis_compile_artifact or basis_materialized_sections."
        )

    slot_routing: dict[str, Any] = {}
    family_routing: dict[str, list[dict[str, Any]]] = {key: [] for key in FAMILY_GROUPS.keys()}
    for slot, expected_family in SLOT_TO_BUILDER_FAMILY.items():
        payload = route_payloads.get(slot, {})
        selection_ids = payload.get("selection_ids", []) if isinstance(payload, dict) else []
        internal_families = payload.get("internal_builder_families", []) if isinstance(payload, dict) else []
        if not isinstance(selection_ids, list):
            raise BasisAssemblyRoutingError(f"Slot '{slot}' selection_ids must be a list.")
        if not isinstance(internal_families, list):
            raise BasisAssemblyRoutingError(f"Slot '{slot}' internal_builder_families must be a list.")
        if len(selection_ids) != len(internal_families):
            raise BasisAssemblyRoutingError(
                f"Slot '{slot}' selection_ids and internal_builder_families must have equal length."
            )

        routes: list[dict[str, str]] = []
        for idx, selection_id in enumerate(selection_ids):
            ui_selection_id = str(selection_id)
            builder_family = str(internal_families[idx])
            if builder_family and builder_family != expected_family:
                raise BasisAssemblyRoutingError(
                    f"Slot '{slot}' maps to invalid builder family '{builder_family}'; expected '{expected_family}'."
                )
            route = {
                "ui_selection_id": ui_selection_id,
                "builder_family": expected_family if not builder_family else builder_family,
            }
            routes.append(route)
            family_routing[_SLOT_TO_GROUP[slot]].append(
                {
                    "slot": slot,
                    "ui_selection_id": route["ui_selection_id"],
                    "builder_family": route["builder_family"],
                }
            )

        slot_routing[slot] = {
            "slot": slot,
            "family_group": _SLOT_TO_GROUP[slot],
            "builder_family": expected_family,
            "routes": routes,
        }

    contract = {
        "version": BASIS_ASSEMBLY_ROUTING_VERSION,
        "slot_routing": slot_routing,
        "family_routing": family_routing,
    }
    contract["routing_hash"] = _stable_hash(contract)
    return contract


def stable_basis_assembly_routing_hash(plan: ExperimentPlan) -> str:
    """Deterministic routing hash derived from basis routing contract."""
    return build_basis_assembly_routing_contract(plan)["routing_hash"]


def stable_basis_assembly_routing_json(plan: ExperimentPlan) -> str:
    """Deterministic routing JSON derived from basis routing contract."""
    return _stable_json(build_basis_assembly_routing_contract(plan))

