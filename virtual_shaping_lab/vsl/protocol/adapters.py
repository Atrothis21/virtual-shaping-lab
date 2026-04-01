"""Adapters between canonical protocol grammar and runtime transport contracts.

Ownership policy (V3.21.0):
- Canonical protocol composition spec lives in `vsl.protocol.spec.ProtocolSpec`
- Runtime transport protocol config lives in `vsl.spec.contracts.ProtocolSpec`
"""

from __future__ import annotations

from typing import Any, Mapping

from virtual_shaping_lab.vsl.protocol.spec import ProtocolSpec as GrammarProtocolSpec
from virtual_shaping_lab.vsl.spec.contracts import ProtocolSpec as RuntimeProtocolSpec


def grammar_to_runtime_protocol_config(spec: GrammarProtocolSpec) -> RuntimeProtocolSpec:
    """Adapt canonical grammar protocol spec into runtime transport protocol config."""
    if not isinstance(spec, GrammarProtocolSpec):
        raise TypeError("spec must be GrammarProtocolSpec.")

    params = {
        "emission_rule": spec.emission_rule,
        "consequence_rule": spec.consequence_rule,
        "advance_rule": spec.advance_rule,
        "stop_rule": spec.stop_rule,
        "protocol_family": spec.protocol_family,
        "action_space_mode": spec.action_space_mode,
        "temporal_mode": spec.temporal_mode,
        "schedule_metadata": dict(spec.schedule_metadata),
        "phase_metadata": dict(spec.phase_metadata),
        "grammar_metadata": dict(spec.metadata),
    }
    return RuntimeProtocolSpec(name=spec.protocol_family, params=params)


def runtime_to_grammar_protocol_spec(
    runtime_spec: RuntimeProtocolSpec,
    *,
    metadata: Mapping[str, Any] | None = None,
) -> GrammarProtocolSpec:
    """Adapt runtime transport protocol config back to canonical grammar protocol spec."""
    if not isinstance(runtime_spec, RuntimeProtocolSpec):
        raise TypeError("runtime_spec must be RuntimeProtocolSpec.")

    params = dict(runtime_spec.params or {})
    protocol_family = str(params.get("protocol_family") or runtime_spec.name or "").strip()
    if not protocol_family:
        protocol_family = "custom"

    merged_meta = dict(metadata or {})
    grammar_meta = params.get("grammar_metadata")
    if isinstance(grammar_meta, Mapping):
        merged_meta.update(dict(grammar_meta))

    schedule_metadata = params.get("schedule_metadata", {})
    if not isinstance(schedule_metadata, Mapping):
        schedule_metadata = {}

    phase_metadata = params.get("phase_metadata", {})
    if not isinstance(phase_metadata, Mapping):
        phase_metadata = {}

    return GrammarProtocolSpec(
        emission_rule=str(params.get("emission_rule") or "scheduled_emission").strip(),
        consequence_rule=str(params.get("consequence_rule") or "deterministic_consequence").strip(),
        advance_rule=str(params.get("advance_rule") or "trial_increment").strip(),
        stop_rule=str(params.get("stop_rule") or "n_trials").strip(),
        protocol_family=protocol_family,
        action_space_mode=str(params.get("action_space_mode") or "classical_none").strip(),
        temporal_mode=str(params.get("temporal_mode") or "trial_discrete").strip(),
        schedule_metadata=dict(schedule_metadata),
        phase_metadata=dict(phase_metadata),
        metadata=merged_meta,
    )
