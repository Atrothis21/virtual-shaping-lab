"""Core V3.2.0 environment-program compilers (slice 2)."""

from __future__ import annotations

from typing import Any

from virtual_shaping_lab.vsl.program.types import EnvironmentProgram, EnvironmentSegment, TrialSpec
from virtual_shaping_lab.vsl.spec import ProgramSpec

_CORE_ACQUISITION_PROTOCOLS = {"acquisition", "acquisition_template"}
_CORE_EXTINCTION_PROTOCOLS = {"nonreinforcement", "nonreinforcement_template", "extinction"}
_CORE_PROTOCOLS = _CORE_ACQUISITION_PROTOCOLS | _CORE_EXTINCTION_PROTOCOLS
_EXTENDED_PROTOCOL_TO_FAMILY = {
    "differential_acquisition": "differential",
    "differential_acquisition_template": "differential",
    "probe": "probe",
    "probe_template": "probe",
    "context_shift": "context_shift",
}
_EXTENDED_PROTOCOLS = set(_EXTENDED_PROTOCOL_TO_FAMILY.keys())
_ALL_COMPILER_PROTOCOLS = _CORE_PROTOCOLS | _EXTENDED_PROTOCOLS


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
    if protocol in _EXTENDED_PROTOCOL_TO_FAMILY:
        return _EXTENDED_PROTOCOL_TO_FAMILY[protocol]
    raise ValueError(
        f"Unsupported protocol '{protocol}' for V3.2 compiler."
    )


def _compile_phase(phase: dict[str, Any], idx: int, *, allowed_protocols: set[str], unsupported_message: str) -> EnvironmentSegment:
    protocol = _normalize_protocol(phase.get("protocol", ""), idx)
    if protocol not in allowed_protocols:
        raise ValueError(unsupported_message.format(protocol=protocol))

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


def _extract_phases(program_spec: ProgramSpec | dict[str, Any]) -> list[dict[str, Any]]:
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
    return phases


def _compile_with_protocol_set(
    program_spec: ProgramSpec | dict[str, Any],
    *,
    allowed_protocols: set[str],
    compiler_label: str,
    unsupported_message: str,
) -> EnvironmentProgram:
    phases = _extract_phases(program_spec)
    segments = [
        _compile_phase(
            _require_phase_mapping(phase, idx),
            idx,
            allowed_protocols=allowed_protocols,
            unsupported_message=unsupported_message,
        )
        for idx, phase in enumerate(phases)
    ]
    return EnvironmentProgram(
        segments=segments,
        metadata={
            "compiler": compiler_label,
            "supported_protocols": sorted(allowed_protocols),
        },
    )


def compile_core_environment_program(program_spec: ProgramSpec | dict[str, Any]) -> EnvironmentProgram:
    """
    Compile core acquisition/extinction phase families into EnvironmentProgram.

    Slice-2 scope:
    - acquisition families
    - nonreinforcement/extinction families
    """

    return _compile_with_protocol_set(
        program_spec,
        allowed_protocols=_CORE_PROTOCOLS,
        compiler_label="v3.2.0-core",
        unsupported_message=(
            "Unsupported protocol '{protocol}' for core compiler. "
            "Supported in slice 2: acquisition/nonreinforcement/extinction families."
        ),
    )


def compile_extended_environment_program(program_spec: ProgramSpec | dict[str, Any]) -> EnvironmentProgram:
    """
    Compile extended differential/probe/context-shift phase families into EnvironmentProgram.

    Slice-3 scope:
    - differential acquisition
    - probe
    - context shift
    """

    return _compile_with_protocol_set(
        program_spec,
        allowed_protocols=_EXTENDED_PROTOCOLS,
        compiler_label="v3.2.0-extended",
        unsupported_message=(
            "Unsupported protocol '{protocol}' for extended compiler. "
            "Supported in slice 3: differential/probe/context-shift families."
        ),
    )


def compile_environment_program(program_spec: ProgramSpec | dict[str, Any]) -> EnvironmentProgram:
    """Compile supported V3.2.0 phase families into one EnvironmentProgram."""

    return _compile_with_protocol_set(
        program_spec,
        allowed_protocols=_ALL_COMPILER_PROTOCOLS,
        compiler_label="v3.2.0-all",
        unsupported_message=(
            "Unsupported protocol '{protocol}' for v3.2 compiler. "
            "Supported: core acquisition/extinction + extended differential/probe/context-shift families."
        ),
    )


def supported_compile_protocols() -> tuple[str, ...]:
    return tuple(sorted(_ALL_COMPILER_PROTOCOLS))
