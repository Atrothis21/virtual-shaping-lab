"""Tuple authoring API helpers: guided catalog + materialization."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from ui.contracts.arrangement_task_agent_composition import (
    ArrangementTaskAgentCompositionError,
    compose_arrangement_task_agent_to_operator_subset,
)
from ui.contracts.arrangement_contract import get_arrangement, list_arrangement_ids
from ui.contracts.agent_bundle_registry import get_agent_bundle, list_agent_bundle_ids
from ui.contracts.operator_plan_materialization import compile_and_materialize_operator_plan
from ui.contracts.task_registry import (
    get_task_registry,
    list_task_ids,
    resolve_task_implementation_for_tuple,
)
from ui.contracts.tuple_authoring_contract import (
    TUPLE_AUTHORING_CONTRACT_VERSION,
    TUPLE_AUTHORING_MODE,
    translate_to_tuple_authoring_payload,
)


class TupleAuthoringAPIError(ValueError):
    """Raised when tuple authoring API helpers fail."""


def _normalize_protocol_family(protocol_family: str) -> str:
    key = str(protocol_family or "").strip().lower()
    if key.startswith("pavlovian_"):
        key = key[len("pavlovian_") :]
    if key.startswith("operant_"):
        key = key[len("operant_") :]
    if key in {"acquisition", "extinction", "differential_acquisition"}:
        return key
    return "acquisition"


def _edit_contract_for_protocol_family(protocol_family: str) -> dict[str, Any]:
    family = _normalize_protocol_family(protocol_family)
    if family == "extinction":
        return {
            "n_acquisition_trials": {"type": "int", "min": 1, "default": 50},
            "n_extinction_trials": {"type": "int", "min": 1, "default": 50},
            "cs_plus": {"type": "list[string]", "min_items": 1, "default": ["tone"]},
        }
    if family == "differential_acquisition":
        return {
            "n_trials": {"type": "int", "min": 1, "default": 100},
            "cs_plus": {"type": "list[string]", "min_items": 1, "default": ["tone"]},
            "cs_minus": {"type": "list[string]", "min_items": 1, "default": ["noise"]},
        }
    return {
        "n_trials": {"type": "int", "min": 1, "default": 100},
        "cs_plus": {"type": "list[string]", "min_items": 1, "default": ["tone"]},
    }


def build_tuple_guided_catalog(
    *,
    arrangement: str | None = None,
    task: str | None = None,
) -> dict[str, Any]:
    """Build guided tuple catalog contract for tuple authoring UI/API."""
    arrangement_ids = list_arrangement_ids()
    task_ids = list_task_ids()
    task_registry = get_task_registry()
    bundles = list_agent_bundle_ids()

    arrangement_key = arrangement.strip().lower() if isinstance(arrangement, str) and arrangement.strip() else None
    task_key = task.strip().lower() if isinstance(task, str) and task.strip() else None

    out_tasks: list[dict[str, Any]] = []
    for task_id in task_ids:
        enabled = False
        implementation_id = None
        protocol_family = None
        if arrangement_key is None:
            enabled = True
        else:
            try:
                impl = resolve_task_implementation_for_tuple(
                    phenomenon_id=task_id,
                    arrangement_id=arrangement_key,
                )
                enabled = True
                implementation_id = impl["id"]
                protocol_family = impl["protocol_family"]
            except Exception:
                enabled = False
        out_tasks.append(
            {
                "id": task_id,
                "enabled": enabled,
                "task_implementation_id": implementation_id,
                "protocol_family": protocol_family,
            }
        )

    out_agents: list[dict[str, Any]] = []
    available_edits: dict[str, Any] = {}
    if arrangement_key and task_key:
        try:
            impl = resolve_task_implementation_for_tuple(
                phenomenon_id=task_key,
                arrangement_id=arrangement_key,
            )
            available_edits = _edit_contract_for_protocol_family(impl["protocol_family"])
            for bundle_id in bundles:
                enabled = True
                reason = None
                try:
                    compose_arrangement_task_agent_to_operator_subset(
                        arrangement_id=arrangement_key,
                        phenomenon_id=task_key,
                        agent_bundle_id=bundle_id,
                    )
                except ArrangementTaskAgentCompositionError as exc:
                    enabled = False
                    reason = str(exc)
                bundle = get_agent_bundle(bundle_id)
                out_agents.append(
                    {
                        "id": bundle_id,
                        "enabled": enabled,
                        "reason": reason,
                        "arrangement_compatibility": list(bundle["arrangement_compatibility"]),
                    }
                )
        except Exception:
            available_edits = {}

    return {
        "contract_version": TUPLE_AUTHORING_CONTRACT_VERSION,
        "authoring_mode": TUPLE_AUTHORING_MODE,
        "arrangements": [
            {"id": arrangement_id, "label": get_arrangement(arrangement_id)["label"]}
            for arrangement_id in arrangement_ids
        ],
        "tasks": out_tasks,
        "agents": out_agents,
        "available_edits": available_edits,
        "registry_generated": True,
        "task_registry_version": task_registry["version"],
    }


def _build_preset_definition_from_composed_subset(
    *,
    arrangement: str,
    task: str,
    agent: str,
    operator_subset: dict[str, Any],
) -> dict[str, Any]:
    return {
        "id": f"tuple_{arrangement}_{task}_{agent}",
        "label": f"{arrangement}/{task}/{agent}",
        "description": "Tuple-composed preset definition.",
        "operator_subset": deepcopy(operator_subset),
        "defaults": {},
        "locked": [],
        "optional": ["a", "c", "g", "e", "pi"],
    }


def _to_stimulus_list(value: Any, *, default: list[str]) -> list[str]:
    if not isinstance(value, list):
        return list(default)
    out = [str(v) for v in value if isinstance(v, str) and str(v).strip()]
    return out or list(default)


def _apply_tuple_edits(payload: dict[str, Any], *, protocol_family: str, edits: dict[str, Any]) -> None:
    phase0 = payload["experiment"]["program"]["phases"][0]
    phase0.setdefault("params", {})
    phase0.setdefault("stimuli", {})

    family = _normalize_protocol_family(protocol_family)
    if family == "extinction":
        n_acq = int(edits.get("n_acquisition_trials", phase0["params"].get("n_acquisition_trials", 50)))
        n_ext = int(edits.get("n_extinction_trials", phase0["params"].get("n_extinction_trials", 50)))
        phase0["params"]["n_acquisition_trials"] = n_acq
        phase0["params"]["n_extinction_trials"] = n_ext
        phase0["trials"] = n_acq + n_ext
        phase0["stimuli"]["cs_plus"] = _to_stimulus_list(
            edits.get("cs_plus"),
            default=list(phase0["stimuli"].get("cs_plus", ["tone"])),
        )
        return

    n_trials = int(edits.get("n_trials", phase0["params"].get("n_trials", 100)))
    phase0["params"]["n_trials"] = n_trials
    phase0["trials"] = n_trials
    phase0["stimuli"]["cs_plus"] = _to_stimulus_list(
        edits.get("cs_plus"),
        default=list(phase0["stimuli"].get("cs_plus", ["tone"])),
    )
    if family == "differential_acquisition":
        phase0["stimuli"]["cs_minus"] = _to_stimulus_list(
            edits.get("cs_minus"),
            default=list(phase0["stimuli"].get("cs_minus", ["noise"])),
        )


def materialize_tuple_authoring_payload(payload: dict[str, Any]) -> dict[str, Any]:
    """Materialize canonical runnable payload from tuple/legacy authoring input."""
    translated = translate_to_tuple_authoring_payload(payload)
    tuple_payload = translated["translated_payload"]
    diagnostics = translated["diagnostics"]
    arrangement = tuple_payload["arrangement"]
    task = tuple_payload["task"]
    agent = tuple_payload["agent"]
    edits = tuple_payload.get("edits", {})

    try:
        composition = compose_arrangement_task_agent_to_operator_subset(
            arrangement_id=arrangement,
            phenomenon_id=task,
            agent_bundle_id=agent,
        )
    except ArrangementTaskAgentCompositionError as exc:
        raise TupleAuthoringAPIError(str(exc)) from exc

    protocol_family = _normalize_protocol_family(composition["provenance"]["protocol_family"])
    stimuli_catalog = _to_stimulus_list(edits.get("cs_plus"), default=["tone"]) + _to_stimulus_list(
        edits.get("cs_minus"), default=["noise"]
    )
    stimuli_catalog = list(dict.fromkeys(stimuli_catalog))

    preset_definition = _build_preset_definition_from_composed_subset(
        arrangement=arrangement,
        task=task,
        agent=agent,
        operator_subset=composition["operator_subset"],
    )
    materialized = compile_and_materialize_operator_plan(
        preset_definition,
        protocol_family=protocol_family,
        stimuli_catalog=stimuli_catalog,
    )
    canonical_payload = {
        "experiment": deepcopy(materialized["experiment"]),
        "report": {"preset": task},
    }
    _apply_tuple_edits(canonical_payload, protocol_family=protocol_family, edits=edits)
    canonical_payload["tuple_authoring"] = {
        "contract_version": TUPLE_AUTHORING_CONTRACT_VERSION,
        "authoring_mode": TUPLE_AUTHORING_MODE,
        "tuple": {
            "arrangement": arrangement,
            "task": task,
            "agent": agent,
        },
        "composition_identity": {
            "composition_hash": composition["provenance"]["composition_hash"],
            "task_implementation_id": composition["provenance"]["task_implementation_id"],
            "protocol_family": composition["provenance"]["protocol_family"],
        },
        "translation_diagnostics": deepcopy(diagnostics),
    }
    return canonical_payload

