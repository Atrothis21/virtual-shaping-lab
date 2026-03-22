"""Preset detail contract materialization for registry-driven teaching UI."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from ui.contracts.operator_registry import get_operator
from ui.contracts.preset_registry import get_preset


class PresetDetailContractError(ValueError):
    """Raised when preset detail contract materialization fails."""


def _as_bool(value: Any, *, label: str) -> bool:
    if not isinstance(value, bool):
        raise PresetDetailContractError(f"{label} must be boolean.")
    return value


def _phase_block(phase: dict[str, Any], *, phase_index: int) -> dict[str, Any]:
    name = str(phase.get("name") or f"Phase {phase_index + 1}").strip()
    protocol = str(phase.get("protocol") or "").strip()
    if not protocol:
        raise PresetDetailContractError(
            f"template.experiment.program.phases[{phase_index}].protocol is required."
        )
    stimuli = phase.get("stimuli") if isinstance(phase.get("stimuli"), dict) else {}
    params = phase.get("params") if isinstance(phase.get("params"), dict) else {}
    return {
        "index": phase_index,
        "name": name,
        "protocol": protocol,
        "stimulus_keys": sorted(stimuli.keys()),
        "parameter_keys": sorted(params.keys()),
        "read_only": True,
    }


def build_preset_detail_contract(preset_id: str) -> dict[str, Any]:
    preset = get_preset(preset_id)
    ui_contract = preset.get("ui_contract")
    if not isinstance(ui_contract, dict):
        raise PresetDetailContractError(f"Preset '{preset_id}' is missing ui_contract.")
    layers = ui_contract.get("layers")
    if not isinstance(layers, dict):
        raise PresetDetailContractError(f"Preset '{preset_id}' ui_contract.layers must be an object.")
    for key in ("overview", "phases", "operators", "math"):
        _as_bool(layers.get(key), label=f"ui_contract.layers.{key}")

    template = preset.get("template")
    if not isinstance(template, dict):
        raise PresetDetailContractError(f"Preset '{preset_id}' is missing template.")
    experiment = template.get("experiment")
    if not isinstance(experiment, dict):
        raise PresetDetailContractError(f"Preset '{preset_id}' template.experiment must be an object.")
    program = experiment.get("program")
    if not isinstance(program, dict):
        raise PresetDetailContractError(f"Preset '{preset_id}' template.experiment.program must be an object.")
    phases = program.get("phases")
    if not isinstance(phases, list) or not phases:
        raise PresetDetailContractError(
            f"Preset '{preset_id}' template.experiment.program.phases must be a non-empty list."
        )

    phase_blocks = [_phase_block(phase, phase_index=idx) for idx, phase in enumerate(phases)]
    phase_summary = " -> ".join(block["protocol"] for block in phase_blocks)

    bindings = preset.get("registry_bindings")
    if not isinstance(bindings, dict):
        raise PresetDetailContractError(f"Preset '{preset_id}' is missing registry_bindings.")
    operator_ids = bindings.get("operators")
    if not isinstance(operator_ids, list) or not operator_ids:
        raise PresetDetailContractError(
            f"Preset '{preset_id}' registry_bindings.operators must be a non-empty list."
        )

    operators: list[dict[str, Any]] = []
    for idx, operator_id in enumerate(operator_ids):
        op = get_operator(str(operator_id))
        runtime = op.get("runtime") if isinstance(op.get("runtime"), dict) else {}
        pedagogy = op.get("pedagogy") if isinstance(op.get("pedagogy"), dict) else {}
        ui = op.get("ui") if isinstance(op.get("ui"), dict) else {}
        operators.append(
            {
                "order": idx,
                "id": op["id"],
                "symbol": op.get("symbol"),
                "name": op.get("name"),
                "family": op.get("family"),
                "stage_index": int(op.get("stage_index", 0)),
                "tooltip": ui.get("tooltip"),
                "short_label": ui.get("short_label"),
                "reads_trialstate": list(runtime.get("reads_trialstate", [])),
                "writes_trialstate": list(runtime.get("writes_trialstate", [])),
                "operator_view": pedagogy.get("operator_view"),
                "algebra": pedagogy.get("algebra"),
                "read_only": True,
            }
        )

    operators = sorted(operators, key=lambda item: (item["stage_index"], item["order"]))
    math_lines = [str(op.get("algebra") or "").strip() for op in operators if str(op.get("algebra") or "").strip()]

    return {
        "preset_id": preset["id"],
        "label": preset.get("label"),
        "description": preset.get("description"),
        "protocol_family": preset.get("protocol_family"),
        "layers": deepcopy(layers),
        "overview": {
            "title": preset.get("label"),
            "description": preset.get("description"),
            "phase_summary": phase_summary,
        },
        "phases": phase_blocks,
        "operators": operators,
        "math": {"lines": math_lines},
        "operator_surface_read_only": True,
    }

