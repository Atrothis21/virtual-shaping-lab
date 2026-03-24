"""Basis-first preset authoring contract for UI editors."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from ui.contracts.operator_basis_registry import list_ui_selectable_implementations
from ui.contracts.operator_plan_materialization import compile_and_materialize_operator_plan
from ui.contracts.preset_registry import get_preset


class PresetBasisAuthoringError(ValueError):
    """Raised when basis-first preset authoring contract validation fails."""


_LEARNING_RULE_TO_W_SELECTION: dict[str, str] = {
    "rescorla_wagner": "rescorla_wagner",
    "temporal_difference": "td0_update",
}

_W_SELECTION_TO_LEARNING_RULE: dict[str, str] = {
    "rescorla_wagner": "rescorla_wagner",
    "td0_update": "temporal_difference",
}


def _require_non_empty_string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise PresetBasisAuthoringError(f"{label} must be a non-empty string.")
    return value


def _require_string_list(value: Any, label: str) -> list[str]:
    if not isinstance(value, list):
        raise PresetBasisAuthoringError(f"{label} must be a list of strings.")
    out: list[str] = []
    for idx, item in enumerate(value):
        out.append(_require_non_empty_string(item, f"{label}[{idx}]"))
    return out


def _canonical_stimuli_catalog(preset: dict[str, Any]) -> list[str]:
    template = preset.get("template", {})
    experiment = template.get("experiment", {}) if isinstance(template, dict) else {}
    program = experiment.get("program", {}) if isinstance(experiment, dict) else {}
    phases = program.get("phases", []) if isinstance(program, dict) else []
    if not isinstance(phases, list) or not phases:
        return ["tone", "noise"]
    phase0 = phases[0] if isinstance(phases[0], dict) else {}
    stimuli = phase0.get("stimuli", {}) if isinstance(phase0, dict) else {}
    cs_plus = stimuli.get("cs_plus", []) if isinstance(stimuli, dict) else []
    catalog = [str(v) for v in cs_plus if isinstance(v, str) and v.strip()]
    if not catalog:
        catalog = ["tone"]
    if "noise" not in catalog:
        catalog.append("noise")
    return catalog


def build_acquisition_basis_authoring_contract() -> dict[str, Any]:
    """Return registry-driven basis authoring contract for acquisition UI."""
    preset = get_preset("acquisition")
    preset_template = preset.get("template", {})
    phase0 = (
        preset_template.get("experiment", {})
        .get("program", {})
        .get("phases", [{}])[0]
    )
    params = phase0.get("params", {}) if isinstance(phase0, dict) else {}
    stimuli = phase0.get("stimuli", {}) if isinstance(phase0, dict) else {}
    cs_plus = stimuli.get("cs_plus", []) if isinstance(stimuli, dict) else []

    basis_definition = preset.get("basis_definition", {})
    operator_subset = basis_definition.get("operator_subset", {}) if isinstance(basis_definition, dict) else {}
    default_phi = str(operator_subset.get("phi", "elemental"))
    default_w = str(operator_subset.get("w", "rescorla_wagner"))
    learning_rule_choices = (
        preset.get("ui_contract", {})
        .get("editability", {})
        .get("option_constraints", {})
        .get("experiment.agent.learning.rule", ["rescorla_wagner", "temporal_difference"])
    )
    if not isinstance(learning_rule_choices, list) or not learning_rule_choices:
        learning_rule_choices = ["rescorla_wagner", "temporal_difference"]

    return {
        "preset_id": "acquisition",
        "protocol_family": "acquisition",
        "registry_generated": True,
        "operator_choices": {
            "phi": list(list_ui_selectable_implementations("phi")),
            "w": list(list_ui_selectable_implementations("w")),
        },
        "defaults": {
            "operator_subset": {
                "phi": default_phi,
                "w": default_w,
            },
            "editable": {
                "n_trials": int(params.get("n_trials", 50)),
                "cs_plus": list(cs_plus) if isinstance(cs_plus, list) else ["tone"],
                "learning_rule": _W_SELECTION_TO_LEARNING_RULE.get(default_w, "rescorla_wagner"),
                "learning_rule_choices": [str(v) for v in learning_rule_choices if isinstance(v, str)],
            },
            "stimuli_catalog": _canonical_stimuli_catalog(preset),
        },
    }


def materialize_acquisition_basis_payload(authoring: dict[str, Any]) -> dict[str, Any]:
    """
    Compile+materialize canonical acquisition payload from basis-first UI input.

    Expected input shape:
    {
      "preset_id": "acquisition",
      "operator_subset": {"phi": "...", "w": "..."},
      "edits": {"n_trials": int, "cs_plus": [...], "learning_rule": "..."}
    }
    """
    if not isinstance(authoring, dict):
        raise PresetBasisAuthoringError("authoring must be an object.")

    preset_id = _require_non_empty_string(authoring.get("preset_id"), "authoring.preset_id")
    if preset_id != "acquisition":
        raise PresetBasisAuthoringError("Only acquisition basis authoring is supported in V3.14 Slice 1.")

    operator_subset = authoring.get("operator_subset", {})
    if not isinstance(operator_subset, dict):
        raise PresetBasisAuthoringError("authoring.operator_subset must be an object.")
    edits = authoring.get("edits", {})
    if not isinstance(edits, dict):
        raise PresetBasisAuthoringError("authoring.edits must be an object.")

    contract = build_acquisition_basis_authoring_contract()
    allowed_phi = set(contract["operator_choices"]["phi"])
    allowed_w = set(contract["operator_choices"]["w"])

    phi = str(operator_subset.get("phi", contract["defaults"]["operator_subset"]["phi"]))
    w = str(operator_subset.get("w", contract["defaults"]["operator_subset"]["w"]))
    if phi not in allowed_phi:
        raise PresetBasisAuthoringError(
            f"authoring.operator_subset.phi must be one of: {', '.join(sorted(allowed_phi))}"
        )
    if w not in allowed_w:
        raise PresetBasisAuthoringError(
            f"authoring.operator_subset.w must be one of: {', '.join(sorted(allowed_w))}"
        )

    if "learning_rule" in edits:
        learning_rule = _require_non_empty_string(edits.get("learning_rule"), "authoring.edits.learning_rule")
        if learning_rule not in _LEARNING_RULE_TO_W_SELECTION:
            allowed_rules = ", ".join(sorted(_LEARNING_RULE_TO_W_SELECTION.keys()))
            raise PresetBasisAuthoringError(
                f"authoring.edits.learning_rule must be one of: {allowed_rules}"
            )
        w = _LEARNING_RULE_TO_W_SELECTION[learning_rule]

    n_trials_raw = edits.get("n_trials", contract["defaults"]["editable"]["n_trials"])
    try:
        n_trials = int(n_trials_raw)
    except (TypeError, ValueError):
        raise PresetBasisAuthoringError("authoring.edits.n_trials must be an integer.")
    if n_trials <= 0:
        raise PresetBasisAuthoringError("authoring.edits.n_trials must be > 0.")

    cs_plus = edits.get("cs_plus", contract["defaults"]["editable"]["cs_plus"])
    cs_plus = _require_string_list(cs_plus, "authoring.edits.cs_plus")
    if not cs_plus:
        raise PresetBasisAuthoringError("authoring.edits.cs_plus must be non-empty.")

    preset = get_preset("acquisition")
    basis_definition = preset.get("basis_definition")
    if not isinstance(basis_definition, dict):
        raise PresetBasisAuthoringError("Preset 'acquisition' is missing basis_definition.")
    preset_definition = deepcopy(basis_definition)
    preset_definition["operator_subset"]["phi"] = phi
    preset_definition["operator_subset"]["w"] = w

    materialized = compile_and_materialize_operator_plan(
        preset_definition,
        protocol_family="acquisition",
        stimuli_catalog=list(cs_plus),
    )
    payload = {
        "experiment": deepcopy(materialized["experiment"]),
        "report": {"preset": "acquisition"},
    }

    phase0 = payload["experiment"]["program"]["phases"][0]
    phase0["stimuli"]["cs_plus"] = list(cs_plus)
    phase0["trials"] = n_trials
    phase0.setdefault("params", {})
    phase0["params"]["n_trials"] = n_trials

    payload["basis_authoring"] = {
        "preset_id": "acquisition",
        "operator_subset": {"phi": phi, "w": w},
        "edits": {
            "n_trials": n_trials,
            "cs_plus": list(cs_plus),
            "learning_rule": _W_SELECTION_TO_LEARNING_RULE.get(w, "rescorla_wagner"),
        },
    }
    return payload
