"""Thin preset registry contract for V3 UI preset mode."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from ui.contracts.dependent_variable_registry import (
    validate_dependent_variable_ids,
    validate_preset_results_contract,
)
from ui.contracts.operator_registry import list_operator_ids
from ui.contracts.trialstate_registry import list_trialstate_field_ids
from ui.contracts.operator_basis_registry import list_ui_selectable_implementations
from ui.contracts.operator_subset_contract import validate_preset_definition
from ui.contracts.task_registry import (
    build_thin_preset_task_reference,
    validate_preset_task_reference,
)


class PresetRegistryValidationError(ValueError):
    """Raised when preset registry contract validation fails."""


PRESET_REGISTRY_VERSION = "3.0"

REQUIRED_PRESET_REGISTRY_KEYS: tuple[str, ...] = ("version", "presets")
REQUIRED_PRESET_KEYS: tuple[str, ...] = (
    "id",
    "label",
    "description",
    "protocol_family",
    "task_reference",
    "basis_definition",
    "template",
    "ui_contract",
    "registry_bindings",
    "results_contract",
)
REQUIRED_PRESET_BINDING_KEYS: tuple[str, ...] = (
    "trialstate_fields",
    "operators",
    "dependent_variables",
)

def _core_basis_definition(*, preset_id: str, label: str, description: str) -> dict[str, Any]:
    return {
        "id": f"rw_{preset_id}",
        "label": f"RW {label}",
        "description": description,
        "operator_subset": {
            "phi": "elemental",
            "p": "state_value",
            "delta": "rw_error",
            "w": "rescorla_wagner",
            "omega": "classical_contingency",
            "m": ["trial_log", "learning_curve", "final_weights"],
        },
        "defaults": {"a": "fixed_alpha"},
        "locked": ["delta", "w"],
        "optional": ["a", "c", "g", "e", "pi"],
        "selectable_universe_source": "operator_basis_registry",
    }


def _core_preset(
    *,
    preset_id: str,
    label: str,
    description: str,
    protocol_family: str,
    phase_name: str,
    phase_protocol: str,
    stimuli: dict[str, Any],
) -> dict[str, Any]:
    return {
        "id": preset_id,
        "label": label,
        "description": description,
        "protocol_family": protocol_family,
        "task_reference": build_thin_preset_task_reference(preset_id),
        "basis_definition": _core_basis_definition(
            preset_id=preset_id,
            label=label,
            description=f"{label} basis subset.",
        ),
        "template": {
            "experiment": {
                "program": {
                    "phases": [
                        {
                            "name": phase_name,
                            "protocol": phase_protocol,
                            "stimuli": deepcopy(stimuli),
                            "params": {"n_trials": 50},
                        }
                    ],
                },
                "agent": {"learning": {"rule": "rescorla_wagner"}},
            }
        },
        "ui_contract": {
            "layers": {
                "overview": True,
                "phases": True,
                "operators": True,
                "math": True,
            },
            "locking": {
                "protocol_locked": True,
                "phase_structure_locked": True,
                "operators_read_only": True,
            },
            "editability": {
                "allowed_parameters": [
                    "experiment.program.phases[0].params.n_trials",
                    "experiment.program.phases[0].stimuli.cs_plus",
                    "experiment.agent.learning.rule",
                ],
                "locked_parameters": [
                    "experiment.program.phases[0].protocol",
                    "experiment.program.phases",
                ],
                "option_constraints": {
                    "experiment.agent.learning.rule": [
                        "rescorla_wagner",
                        "temporal_difference",
                    ]
                },
            },
        },
        "registry_bindings": {
            "trialstate_fields": [
                "stimulus",
                "prediction",
                "outcome",
                "error",
                "weights",
                "trial_index",
                "phase_name",
            ],
            "operators": ["phi", "p", "delta", "w", "m"],
            "dependent_variables": [
                "associative_strength",
                "predicted_outcome",
                "prediction_error",
                "response_strength",
            ],
        },
        "results_contract": {
            "primary_dependent_variables": [
                "associative_strength",
                "predicted_outcome",
                "prediction_error",
            ],
            "secondary_dependent_variables": ["response_strength"],
            "graph_priority": [
                "associative_strength",
                "predicted_outcome",
                "prediction_error",
                "response_strength",
            ],
            "measurement_readouts": [
                "trial_log",
                "learning_curve",
                "report_bundle",
            ],
        },
    }


_acquisition = _core_preset(
    preset_id="acquisition",
    label="Acquisition",
    description="Canonical acquisition preset contract surface.",
    protocol_family="acquisition",
    phase_name="Acquisition",
    phase_protocol="acquisition",
    stimuli={"cs_plus": ["tone"]},
)
_extinction = _core_preset(
    preset_id="extinction",
    label="Extinction",
    description="Canonical extinction preset contract surface.",
    protocol_family="extinction",
    phase_name="Extinction",
    phase_protocol="extinction",
    stimuli={"cs_plus": ["tone"]},
)
_differential = _core_preset(
    preset_id="differential_acquisition",
    label="Differential Acquisition",
    description="Canonical differential acquisition preset contract surface.",
    protocol_family="differential_acquisition",
    phase_name="Differential Acquisition",
    phase_protocol="differential_acquisition",
    stimuli={"cs_plus": ["tone"], "cs_minus": ["noise"]},
)

_differential["ui_contract"]["editability"]["allowed_parameters"].append(
    "experiment.program.phases[0].stimuli.cs_minus"
)

PRESET_REGISTRY: dict[str, Any] = {
    "version": PRESET_REGISTRY_VERSION,
    "presets": {
        "acquisition": _acquisition,
        "extinction": _extinction,
        "differential_acquisition": _differential,
    },
}


def _require_dict(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise PresetRegistryValidationError(f"{label} must be an object.")
    return value


def _require_non_empty_string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise PresetRegistryValidationError(f"{label} must be a non-empty string.")
    return value


def _require_string_list(value: Any, label: str) -> list[str]:
    if not isinstance(value, list):
        raise PresetRegistryValidationError(f"{label} must be a list of strings.")
    out: list[str] = []
    for idx, item in enumerate(value):
        out.append(_require_non_empty_string(item, f"{label}[{idx}]"))
    return out


def _validate_preset_ui_contract(
    ui_contract: dict[str, Any],
    *,
    preset_key: str,
) -> None:
    layers = _require_dict(
        ui_contract.get("layers"),
        f"preset_registry.presets.{preset_key}.ui_contract.layers",
    )
    for layer_key in ("overview", "phases", "operators", "math"):
        if layer_key not in layers:
            raise PresetRegistryValidationError(
                f"preset_registry.presets.{preset_key}.ui_contract.layers missing required key: {layer_key}"
            )
        if not isinstance(layers.get(layer_key), bool):
            raise PresetRegistryValidationError(
                f"preset_registry.presets.{preset_key}.ui_contract.layers.{layer_key} must be boolean."
            )

    locking = _require_dict(
        ui_contract.get("locking"),
        f"preset_registry.presets.{preset_key}.ui_contract.locking",
    )
    for lock_key in ("protocol_locked", "phase_structure_locked", "operators_read_only"):
        if lock_key not in locking:
            raise PresetRegistryValidationError(
                f"preset_registry.presets.{preset_key}.ui_contract.locking missing required key: {lock_key}"
            )
        if not isinstance(locking.get(lock_key), bool):
            raise PresetRegistryValidationError(
                f"preset_registry.presets.{preset_key}.ui_contract.locking.{lock_key} must be boolean."
            )

    editability = _require_dict(
        ui_contract.get("editability"),
        f"preset_registry.presets.{preset_key}.ui_contract.editability",
    )
    allowed = set(
        _require_string_list(
            editability.get("allowed_parameters"),
            f"preset_registry.presets.{preset_key}.ui_contract.editability.allowed_parameters",
        )
    )
    locked = set(
        _require_string_list(
            editability.get("locked_parameters"),
            f"preset_registry.presets.{preset_key}.ui_contract.editability.locked_parameters",
        )
    )
    overlap = sorted(allowed.intersection(locked))
    if overlap:
        raise PresetRegistryValidationError(
            f"preset_registry.presets.{preset_key}.ui_contract.editability has overlapping allowed/locked parameters: {', '.join(overlap)}"
        )
    option_constraints = editability.get("option_constraints", {})
    if option_constraints is not None:
        option_constraints = _require_dict(
            option_constraints,
            f"preset_registry.presets.{preset_key}.ui_contract.editability.option_constraints",
        )
        for path, values in option_constraints.items():
            path_key = _require_non_empty_string(
                path,
                f"preset_registry.presets.{preset_key}.ui_contract.editability.option_constraints.path",
            )
            if path_key not in allowed:
                raise PresetRegistryValidationError(
                    f"preset_registry.presets.{preset_key}.ui_contract.editability.option_constraints path must also be allowed: {path_key}"
                )
            allowed_values = _require_string_list(
                values,
                f"preset_registry.presets.{preset_key}.ui_contract.editability.option_constraints.{path_key}",
            )
            if not allowed_values:
                raise PresetRegistryValidationError(
                    f"preset_registry.presets.{preset_key}.ui_contract.editability.option_constraints.{path_key} must be non-empty."
                )


def _validate_acquisition_template(preset: dict[str, Any], *, preset_key: str) -> None:
    template = _require_dict(
        preset.get("template"),
        f"preset_registry.presets.{preset_key}.template",
    )
    experiment = _require_dict(
        template.get("experiment"),
        f"preset_registry.presets.{preset_key}.template.experiment",
    )
    program = _require_dict(
        experiment.get("program"),
        f"preset_registry.presets.{preset_key}.template.experiment.program",
    )
    phases = program.get("phases")
    if not isinstance(phases, list):
        raise PresetRegistryValidationError(
            f"preset_registry.presets.{preset_key}.template.experiment.program.phases must be a list."
        )
    if len(phases) != 1:
        raise PresetRegistryValidationError(
            f"preset_registry.presets.{preset_key} acquisition invariant failed: expected exactly one phase."
        )
    phase0 = _require_dict(
        phases[0],
        f"preset_registry.presets.{preset_key}.template.experiment.program.phases[0]",
    )
    protocol = _require_non_empty_string(
        phase0.get("protocol"),
        f"preset_registry.presets.{preset_key}.template.experiment.program.phases[0].protocol",
    )
    if protocol != "acquisition":
        raise PresetRegistryValidationError(
            f"preset_registry.presets.{preset_key} acquisition invariant failed: phase protocol must be 'acquisition'."
        )


def validate_acquisition_preset_invariants(
    preset: dict[str, Any],
    *,
    preset_key: str = "acquisition",
) -> None:
    protocol_family = _require_non_empty_string(
        preset.get("protocol_family"),
        f"preset_registry.presets.{preset_key}.protocol_family",
    )
    if protocol_family != "acquisition":
        raise PresetRegistryValidationError(
            f"preset_registry.presets.{preset_key} acquisition invariant failed: protocol_family must be 'acquisition'."
        )

    _validate_acquisition_template(preset, preset_key=preset_key)

    bindings = _require_dict(
        preset.get("registry_bindings"),
        f"preset_registry.presets.{preset_key}.registry_bindings",
    )
    operators = set(
        _require_string_list(
            bindings.get("operators"),
            f"preset_registry.presets.{preset_key}.registry_bindings.operators",
        )
    )
    required_operators = {"phi", "p", "delta", "w", "m"}
    missing = sorted(required_operators - operators)
    if missing:
        raise PresetRegistryValidationError(
            f"preset_registry.presets.{preset_key} acquisition invariant failed: missing required operators: {', '.join(missing)}"
        )


def validate_preset_registry(registry: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = deepcopy(PRESET_REGISTRY if registry is None else registry)
    root = _require_dict(payload, "preset_registry")

    for key in REQUIRED_PRESET_REGISTRY_KEYS:
        if key not in root:
            raise PresetRegistryValidationError(f"preset_registry missing required key: {key}")

    _require_non_empty_string(root.get("version"), "preset_registry.version")
    presets = _require_dict(root.get("presets"), "preset_registry.presets")

    known_trialstate_fields = set(list_trialstate_field_ids())
    known_operators = set(list_operator_ids())

    seen_ids: set[str] = set()
    for preset_key, raw_preset in presets.items():
        preset = _require_dict(raw_preset, f"preset_registry.presets.{preset_key}")
        for key in REQUIRED_PRESET_KEYS:
            if key not in preset:
                raise PresetRegistryValidationError(
                    f"preset_registry.presets.{preset_key} missing required key: {key}"
                )
        preset_id = _require_non_empty_string(
            preset.get("id"), f"preset_registry.presets.{preset_key}.id"
        )
        if preset_id in seen_ids:
            raise PresetRegistryValidationError(
                f"preset_registry has duplicate preset id: {preset_id}"
            )
        seen_ids.add(preset_id)
        if preset_id != preset_key:
            raise PresetRegistryValidationError(
                f"preset_registry.presets.{preset_key}.id must match preset key '{preset_key}'."
            )
        _require_non_empty_string(
            preset.get("label"), f"preset_registry.presets.{preset_key}.label"
        )
        _require_non_empty_string(
            preset.get("description"), f"preset_registry.presets.{preset_key}.description"
        )
        _require_non_empty_string(
            preset.get("protocol_family"),
            f"preset_registry.presets.{preset_key}.protocol_family",
        )
        task_reference = _require_dict(
            preset.get("task_reference"),
            f"preset_registry.presets.{preset_key}.task_reference",
        )
        try:
            validate_preset_task_reference(task_reference)
        except Exception as exc:
            raise PresetRegistryValidationError(
                f"preset_registry.presets.{preset_key}.task_reference invalid: {exc}"
            ) from exc
        basis_definition = _require_dict(
            preset.get("basis_definition"),
            f"preset_registry.presets.{preset_key}.basis_definition",
        )
        selectable_universe_source = _require_non_empty_string(
            basis_definition.get("selectable_universe_source"),
            f"preset_registry.presets.{preset_key}.basis_definition.selectable_universe_source",
        )
        if selectable_universe_source != "operator_basis_registry":
            raise PresetRegistryValidationError(
                f"preset_registry.presets.{preset_key}.basis_definition.selectable_universe_source "
                "must be 'operator_basis_registry'."
            )
        try:
            validate_preset_definition(basis_definition)
        except Exception as exc:
            raise PresetRegistryValidationError(
                f"preset_registry.presets.{preset_key}.basis_definition invalid: {exc}"
            ) from exc
        _validate_preset_ui_contract(
            _require_dict(
                preset.get("ui_contract"),
                f"preset_registry.presets.{preset_key}.ui_contract",
            ),
            preset_key=preset_key,
        )

        bindings = _require_dict(
            preset.get("registry_bindings"),
            f"preset_registry.presets.{preset_key}.registry_bindings",
        )
        for key in REQUIRED_PRESET_BINDING_KEYS:
            if key not in bindings:
                raise PresetRegistryValidationError(
                    f"preset_registry.presets.{preset_key}.registry_bindings missing required key: {key}"
                )

        trial_fields = _require_string_list(
            bindings.get("trialstate_fields"),
            f"preset_registry.presets.{preset_key}.registry_bindings.trialstate_fields",
        )
        operators = _require_string_list(
            bindings.get("operators"),
            f"preset_registry.presets.{preset_key}.registry_bindings.operators",
        )
        dependent_variables = validate_dependent_variable_ids(
            bindings.get("dependent_variables"),
            label=f"preset_registry.presets.{preset_key}.registry_bindings.dependent_variables",
        )

        for field in trial_fields:
            if field not in known_trialstate_fields:
                raise PresetRegistryValidationError(
                    f"preset_registry.presets.{preset_key}.registry_bindings.trialstate_fields "
                    f"references unknown TrialState field: {field}"
                )
        for operator in operators:
            if operator not in known_operators:
                raise PresetRegistryValidationError(
                    f"preset_registry.presets.{preset_key}.registry_bindings.operators "
                    f"references unknown operator id: {operator}"
                )

        try:
            results_contract = validate_preset_results_contract(
                _require_dict(
                    preset.get("results_contract"),
                    f"preset_registry.presets.{preset_key}.results_contract",
                )
            )
        except Exception as exc:
            raise PresetRegistryValidationError(
                f"preset_registry.presets.{preset_key}.results_contract invalid: {exc}"
            ) from exc
        declared_variables = set(dependent_variables)
        for contract_key in (
            "primary_dependent_variables",
            "secondary_dependent_variables",
            "graph_priority",
        ):
            for variable_id in results_contract[contract_key]:
                if variable_id not in declared_variables:
                    raise PresetRegistryValidationError(
                        f"preset_registry.presets.{preset_key}.results_contract.{contract_key} "
                        f"contains undeclared dependent variable: {variable_id}"
                    )
        if preset_key == "acquisition":
            validate_acquisition_preset_invariants(preset, preset_key=preset_key)

        known_measurement_readouts = set(list_ui_selectable_implementations("m"))
        measurement_readouts = results_contract.get("measurement_readouts", [])
        if measurement_readouts is not None:
            if not isinstance(measurement_readouts, list):
                raise PresetRegistryValidationError(
                    f"preset_registry.presets.{preset_key}.results_contract.measurement_readouts must be a list."
                )
            for idx, readout_id in enumerate(measurement_readouts):
                key = _require_non_empty_string(
                    readout_id,
                    f"preset_registry.presets.{preset_key}.results_contract.measurement_readouts[{idx}]",
                )
                if key not in known_measurement_readouts:
                    raise PresetRegistryValidationError(
                        f"preset_registry.presets.{preset_key}.results_contract.measurement_readouts[{idx}] "
                        f"references unknown measurement readout id: {key}"
                    )

    return payload


def get_preset_registry() -> dict[str, Any]:
    return validate_preset_registry(PRESET_REGISTRY)


def list_preset_ids() -> tuple[str, ...]:
    payload = get_preset_registry()
    return tuple(sorted(payload["presets"].keys()))


def get_preset(preset_id: str) -> dict[str, Any]:
    key = _require_non_empty_string(preset_id, "preset_id")
    payload = get_preset_registry()
    presets = payload["presets"]
    if key not in presets:
        available = ", ".join(sorted(presets.keys()))
        raise KeyError(f"Unknown preset '{key}'. Available presets: {available}")
    return deepcopy(presets[key])
