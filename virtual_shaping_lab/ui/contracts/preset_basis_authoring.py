"""Basis-first preset authoring contract for UI editors."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from ui.contracts.operator_basis_registry import list_ui_selectable_implementations
from ui.contracts.operator_plan_materialization import compile_and_materialize_operator_plan
from ui.contracts.preset_registry import get_preset


class PresetBasisAuthoringError(ValueError):
    """Raised when basis-first preset authoring contract validation fails."""


_CORE_BASIS_PRESETS: tuple[str, ...] = (
    "acquisition",
    "extinction",
    "differential_acquisition",
)

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

    values: list[str] = []
    for key in ("cs_plus", "cs_minus"):
        entries = stimuli.get(key, []) if isinstance(stimuli, dict) else []
        if isinstance(entries, list):
            values.extend(str(v) for v in entries if isinstance(v, str) and v.strip())
    deduped = list(dict.fromkeys(values))
    if not deduped:
        deduped = ["tone"]
    if "noise" not in deduped:
        deduped.append("noise")
    return deduped


def _editable_defaults_for_preset(preset_id: str, phase0: dict[str, Any], default_w: str) -> dict[str, Any]:
    params = phase0.get("params", {}) if isinstance(phase0, dict) else {}
    stimuli = phase0.get("stimuli", {}) if isinstance(phase0, dict) else {}
    cs_plus = list(stimuli.get("cs_plus", ["tone"])) if isinstance(stimuli.get("cs_plus"), list) else ["tone"]

    if preset_id == "acquisition":
        return {
            "n_trials": int(params.get("n_trials", 50)),
            "cs_plus": cs_plus,
            "learning_rule": _W_SELECTION_TO_LEARNING_RULE.get(default_w, "rescorla_wagner"),
        }
    if preset_id == "extinction":
        return {
            "n_acquisition_trials": int(params.get("n_acquisition_trials", 50)),
            "n_extinction_trials": int(params.get("n_extinction_trials", 50)),
            "cs_plus": cs_plus,
            "learning_rule": _W_SELECTION_TO_LEARNING_RULE.get(default_w, "rescorla_wagner"),
        }
    if preset_id == "differential_acquisition":
        cs_minus = list(stimuli.get("cs_minus", ["noise"])) if isinstance(stimuli.get("cs_minus"), list) else ["noise"]
        return {
            "n_trials": int(params.get("n_trials", 50)),
            "cs_plus": cs_plus,
            "cs_minus": cs_minus,
            "learning_rule": _W_SELECTION_TO_LEARNING_RULE.get(default_w, "rescorla_wagner"),
        }
    raise PresetBasisAuthoringError(f"Unsupported basis authoring preset: {preset_id}")


def build_preset_basis_authoring_contract(preset_id: str) -> dict[str, Any]:
    """Return registry-driven basis authoring contract for a core basis preset."""
    preset_key = _require_non_empty_string(preset_id, "preset_id").lower()
    if preset_key not in _CORE_BASIS_PRESETS:
        raise PresetBasisAuthoringError(
            f"Unsupported basis authoring preset '{preset_key}'. Supported presets: {', '.join(_CORE_BASIS_PRESETS)}"
        )

    preset = get_preset(preset_key)
    preset_template = preset.get("template", {})
    phase0 = (
        preset_template.get("experiment", {})
        .get("program", {})
        .get("phases", [{}])[0]
    )

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

    editable_defaults = _editable_defaults_for_preset(preset_key, phase0, default_w)
    editable_defaults["learning_rule_choices"] = [str(v) for v in learning_rule_choices if isinstance(v, str)]

    return {
        "preset_id": preset_key,
        "protocol_family": str(preset.get("protocol_family", preset_key)),
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
            "editable": editable_defaults,
            "stimuli_catalog": _canonical_stimuli_catalog(preset),
        },
    }


def _materialize_phase_edits(preset_id: str, phase0: dict[str, Any], edits: dict[str, Any], defaults: dict[str, Any]) -> dict[str, Any]:
    if preset_id in {"acquisition", "differential_acquisition"}:
        n_trials_raw = edits.get("n_trials", defaults["n_trials"])
        try:
            n_trials = int(n_trials_raw)
        except (TypeError, ValueError):
            raise PresetBasisAuthoringError("authoring.edits.n_trials must be an integer.")
        if n_trials <= 0:
            raise PresetBasisAuthoringError("authoring.edits.n_trials must be > 0.")
        phase0["trials"] = n_trials
        phase0.setdefault("params", {})
        phase0["params"]["n_trials"] = n_trials
        out: dict[str, Any] = {"n_trials": n_trials}
    else:
        n_acq_raw = edits.get("n_acquisition_trials", defaults["n_acquisition_trials"])
        n_ext_raw = edits.get("n_extinction_trials", defaults["n_extinction_trials"])
        try:
            n_acq = int(n_acq_raw)
            n_ext = int(n_ext_raw)
        except (TypeError, ValueError):
            raise PresetBasisAuthoringError(
                "authoring.edits.n_acquisition_trials and n_extinction_trials must be integers."
            )
        if n_acq <= 0 or n_ext <= 0:
            raise PresetBasisAuthoringError(
                "authoring.edits.n_acquisition_trials and n_extinction_trials must be > 0."
            )
        phase0["trials"] = n_acq + n_ext
        phase0.setdefault("params", {})
        phase0["params"]["n_acquisition_trials"] = n_acq
        phase0["params"]["n_extinction_trials"] = n_ext
        out = {
            "n_acquisition_trials": n_acq,
            "n_extinction_trials": n_ext,
        }
    return out


def materialize_preset_basis_payload(authoring: dict[str, Any]) -> dict[str, Any]:
    """Compile+materialize canonical payload from basis-first UI input."""
    if not isinstance(authoring, dict):
        raise PresetBasisAuthoringError("authoring must be an object.")

    preset_id = _require_non_empty_string(authoring.get("preset_id"), "authoring.preset_id").lower()
    contract = build_preset_basis_authoring_contract(preset_id)
    defaults = contract["defaults"]["editable"]

    operator_subset = authoring.get("operator_subset", {})
    if not isinstance(operator_subset, dict):
        raise PresetBasisAuthoringError("authoring.operator_subset must be an object.")
    edits = authoring.get("edits", {})
    if not isinstance(edits, dict):
        raise PresetBasisAuthoringError("authoring.edits must be an object.")

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

    learning_rule = edits.get("learning_rule", defaults["learning_rule"])
    learning_rule = _require_non_empty_string(learning_rule, "authoring.edits.learning_rule")
    if learning_rule not in _LEARNING_RULE_TO_W_SELECTION:
        allowed_rules = ", ".join(sorted(_LEARNING_RULE_TO_W_SELECTION.keys()))
        raise PresetBasisAuthoringError(
            f"authoring.edits.learning_rule must be one of: {allowed_rules}"
        )
    w = _LEARNING_RULE_TO_W_SELECTION[learning_rule]

    cs_plus = _require_string_list(edits.get("cs_plus", defaults["cs_plus"]), "authoring.edits.cs_plus")
    if not cs_plus:
        raise PresetBasisAuthoringError("authoring.edits.cs_plus must be non-empty.")
    cs_minus: list[str] = []
    if preset_id == "differential_acquisition":
        cs_minus = _require_string_list(edits.get("cs_minus", defaults["cs_minus"]), "authoring.edits.cs_minus")
        if not cs_minus:
            raise PresetBasisAuthoringError("authoring.edits.cs_minus must be non-empty.")

    stimuli_catalog = list(dict.fromkeys([*cs_plus, *cs_minus])) or list(contract["defaults"]["stimuli_catalog"])

    preset = get_preset(preset_id)
    basis_definition = preset.get("basis_definition")
    if not isinstance(basis_definition, dict):
        raise PresetBasisAuthoringError(f"Preset '{preset_id}' is missing basis_definition.")
    preset_definition = deepcopy(basis_definition)
    preset_definition["operator_subset"]["phi"] = phi
    preset_definition["operator_subset"]["w"] = w

    materialized = compile_and_materialize_operator_plan(
        preset_definition,
        protocol_family=contract["protocol_family"],
        stimuli_catalog=stimuli_catalog,
    )
    payload = {
        "experiment": deepcopy(materialized["experiment"]),
        "report": {"preset": preset_id},
    }

    phase0 = payload["experiment"]["program"]["phases"][0]
    phase0.setdefault("stimuli", {})
    phase0["stimuli"]["cs_plus"] = list(cs_plus)
    edit_snapshot = _materialize_phase_edits(preset_id, phase0, edits, defaults)
    if preset_id == "differential_acquisition":
        phase0["stimuli"]["cs_minus"] = list(cs_minus)
        edit_snapshot["cs_minus"] = list(cs_minus)

    edit_snapshot["cs_plus"] = list(cs_plus)
    edit_snapshot["learning_rule"] = _W_SELECTION_TO_LEARNING_RULE.get(w, "rescorla_wagner")
    payload["basis_authoring"] = {
        "preset_id": preset_id,
        "operator_subset": {"phi": phi, "w": w},
        "edits": edit_snapshot,
    }
    return payload


def build_acquisition_basis_authoring_contract() -> dict[str, Any]:
    return build_preset_basis_authoring_contract("acquisition")


def build_extinction_basis_authoring_contract() -> dict[str, Any]:
    return build_preset_basis_authoring_contract("extinction")


def build_differential_acquisition_basis_authoring_contract() -> dict[str, Any]:
    return build_preset_basis_authoring_contract("differential_acquisition")


def materialize_acquisition_basis_payload(authoring: dict[str, Any]) -> dict[str, Any]:
    return materialize_preset_basis_payload(authoring)


def materialize_extinction_basis_payload(authoring: dict[str, Any]) -> dict[str, Any]:
    return materialize_preset_basis_payload(authoring)


def materialize_differential_acquisition_basis_payload(authoring: dict[str, Any]) -> dict[str, Any]:
    return materialize_preset_basis_payload(authoring)
