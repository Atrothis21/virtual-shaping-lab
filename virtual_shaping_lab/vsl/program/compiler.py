"""Core V3.2.0 environment-program compilers (slice 2)."""

from __future__ import annotations

from typing import Any

from virtual_shaping_lab.vsl.program.types import EnvironmentProgram, EnvironmentSegment, TrialSpec
from virtual_shaping_lab.vsl.spec import ProgramSpec

_CORE_ACQUISITION_PROTOCOLS = {"acquisition", "acquisition_template"}
_CORE_EXTINCTION_PROTOCOLS = {"nonreinforcement", "nonreinforcement_template", "extinction"}
_CORE_PROTOCOLS = _CORE_ACQUISITION_PROTOCOLS | _CORE_EXTINCTION_PROTOCOLS


def _require_phase_mapping(phase: Any, idx: int) -> dict[str, Any]:
    if not isinstance(phase, dict):
        raise ValueError(f"program.phases[{idx}] must be an object.")
    return phase


def _trial_count(phase: dict[str, Any]) -> int:
    params = phase.get("params", {})
    if not isinstance(params, dict):
        params = {}
    raw = phase.get("trials", params.get("n_trials", 1))
    try:
        value = int(raw)
    except (TypeError, ValueError) as exc:
        raise ValueError("phase trial count must be an integer.") from exc
    if value <= 0:
        raise ValueError("phase trial count must be > 0.")
    return value


def _normalize_protocol(raw_protocol: Any, idx: int) -> str:
    protocol = str(raw_protocol or "").strip().lower()
    if not protocol:
        raise ValueError(f"program.phases[{idx}].protocol must be a non-empty string.")
    return protocol


def _segment_family(protocol: str) -> str:
    if protocol in _CORE_ACQUISITION_PROTOCOLS:
        return "acquisition"
    if protocol in _CORE_EXTINCTION_PROTOCOLS:
        return "extinction"
    raise ValueError(
        f"Unsupported protocol '{protocol}' for core compiler. "
        "Supported in slice 2: acquisition/nonreinforcement/extinction families."
    )


def _compile_phase(phase: dict[str, Any], idx: int) -> EnvironmentSegment:
    protocol = _normalize_protocol(phase.get("protocol", ""), idx)
    if protocol not in _CORE_PROTOCOLS:
        raise ValueError(
            f"Unsupported protocol '{protocol}' for core compiler. "
            "Supported in slice 2: acquisition/nonreinforcement/extinction families."
        )

    params = phase.get("params", {})
    if not isinstance(params, dict):
        raise ValueError(f"program.phases[{idx}].params must be an object.")

    stimuli = phase.get("stimuli", {})
    if not isinstance(stimuli, dict):
        raise ValueError(f"program.phases[{idx}].stimuli must be an object.")

    n_trials = _trial_count(phase)
    family = _segment_family(protocol)
    trial = TrialSpec(
        trial_type=f"{protocol}_trial",
        n_trials=n_trials,
        stimuli=dict(stimuli),
        params=dict(params),
        events=[],
        metadata={"family": family, "phase_index": idx},
    )
    return EnvironmentSegment(
        key=f"{protocol}_{idx}",
        name=str(phase.get("name") or f"Phase {idx + 1}"),
        protocol=protocol,
        trials=[trial],
        metadata={"family": family, "phase_index": idx},
    )


def compile_core_environment_program(program_spec: ProgramSpec | dict[str, Any]) -> EnvironmentProgram:
    """
    Compile core acquisition/extinction phase families into EnvironmentProgram.

    Slice-2 scope:
    - acquisition families
    - nonreinforcement/extinction families
    """

    if isinstance(program_spec, ProgramSpec):
        phases = list(program_spec.phases)
    elif isinstance(program_spec, dict):
        raw_phases = program_spec.get("phases", [])
        if raw_phases is None:
            raw_phases = []
        if not isinstance(raw_phases, list):
            raise ValueError("program_spec.phases must be a list.")
        phases = list(raw_phases)
    else:
        raise ValueError("program_spec must be a ProgramSpec or object with phases.")

    if not phases:
        raise ValueError("program_spec.phases must be non-empty.")

    segments = [_compile_phase(_require_phase_mapping(phase, idx), idx) for idx, phase in enumerate(phases)]
    return EnvironmentProgram(
        segments=segments,
        metadata={
            "compiler": "v3.2.0-core",
            "supported_protocols": sorted(_CORE_PROTOCOLS),
        },
    )
