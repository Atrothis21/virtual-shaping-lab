"""Protocol instantiation boundary from grammar tuples to typed contracts.

V3.21.0 slice 4 scope:
- enforce protocol legality before materialization
- expose deterministic typed boundary payload for runtime assembly
- provide machine-readable failure catalog and errors
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping

from .adapters import grammar_to_runtime_protocol_config, runtime_to_grammar_protocol_spec
from .spec import ProtocolSpec
from .validation import ProtocolSpecValidationError
from virtual_shaping_lab.vsl.spec.contracts import ProtocolSpec as RuntimeProtocolConfig


PROTO_INSTANTIATION_FAILURES: dict[str, str] = {
    "INST_E_INVALID_SPEC_INPUT": "Protocol spec input must be ProtocolSpec or object payload.",
    "INST_E_LEGALITY": "Protocol spec failed legality validation before materialization.",
    "INST_E_BOUNDARY_RESOLUTION": "Protocol boundary resolution failed for legacy/runtime inputs.",
}


@dataclass
class ProtocolInstantiationError(ValueError):
    code: str
    message: str
    details: dict[str, Any] = field(default_factory=dict)

    def __str__(self) -> str:
        return f"[{self.code}] {self.message}"


@dataclass(frozen=True)
class ProtocolOperatorHandle:
    slot: str
    variant: str
    params: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.slot, str) or not self.slot.strip():
            raise ValueError("ProtocolOperatorHandle.slot must be a non-empty string.")
        if not isinstance(self.variant, str) or not self.variant.strip():
            raise ValueError("ProtocolOperatorHandle.variant must be a non-empty string.")
        if not isinstance(self.params, dict):
            raise ValueError("ProtocolOperatorHandle.params must be an object.")


@dataclass(frozen=True)
class ProtocolInstantiationArtifact:
    protocol_spec: ProtocolSpec
    runtime_config: RuntimeProtocolConfig
    emission_operator: ProtocolOperatorHandle
    consequence_operator: ProtocolOperatorHandle
    advance_operator: ProtocolOperatorHandle
    stop_operator: ProtocolOperatorHandle
    protocol_family: str
    action_space_mode: str
    temporal_mode: str


def _coerce_protocol_spec(spec: ProtocolSpec | Mapping[str, Any]) -> ProtocolSpec:
    if isinstance(spec, ProtocolSpec):
        return spec
    if isinstance(spec, Mapping):
        try:
            return ProtocolSpec.from_dict(dict(spec))
        except (ProtocolSpecValidationError, ValueError, TypeError) as exc:
            raise ProtocolInstantiationError(
                "INST_E_LEGALITY",
                PROTO_INSTANTIATION_FAILURES["INST_E_LEGALITY"],
                details={"reason": str(exc)},
            ) from exc
    raise ProtocolInstantiationError(
        "INST_E_INVALID_SPEC_INPUT",
        PROTO_INSTANTIATION_FAILURES["INST_E_INVALID_SPEC_INPUT"],
    )


def instantiate_protocol_contracts(spec: ProtocolSpec | Mapping[str, Any]) -> ProtocolInstantiationArtifact:
    """Materialize typed protocol boundary contracts from canonical grammar spec."""
    protocol_spec = _coerce_protocol_spec(spec)
    runtime_config = grammar_to_runtime_protocol_config(protocol_spec)
    return ProtocolInstantiationArtifact(
        protocol_spec=protocol_spec,
        runtime_config=runtime_config,
        emission_operator=ProtocolOperatorHandle(slot="Omega_emission", variant=protocol_spec.emission_rule),
        consequence_operator=ProtocolOperatorHandle(slot="Omega_consequence", variant=protocol_spec.consequence_rule),
        advance_operator=ProtocolOperatorHandle(slot="Omega_advance", variant=protocol_spec.advance_rule),
        stop_operator=ProtocolOperatorHandle(slot="Omega_stop", variant=protocol_spec.stop_rule),
        protocol_family=protocol_spec.protocol_family,
        action_space_mode=protocol_spec.action_space_mode,
        temporal_mode=protocol_spec.temporal_mode,
    )


def instantiate_protocol_from_boundary(
    *,
    protocol_rule: Any,
    protocol_config: Mapping[str, Any] | None = None,
    metadata: Mapping[str, Any] | None = None,
) -> ProtocolInstantiationArtifact:
    """Resolve boundary protocol inputs and materialize typed protocol contracts."""
    try:
        params = dict(protocol_config or {})
        if "protocol_family" not in params:
            params["protocol_family"] = protocol_rule
        runtime_spec = RuntimeProtocolConfig(name=str(protocol_rule), params=params)
        resolved = runtime_to_grammar_protocol_spec(runtime_spec, metadata=metadata)
    except Exception as exc:
        raise ProtocolInstantiationError(
            "INST_E_BOUNDARY_RESOLUTION",
            PROTO_INSTANTIATION_FAILURES["INST_E_BOUNDARY_RESOLUTION"],
            details={"reason": str(exc)},
        ) from exc
    return instantiate_protocol_contracts(resolved)
