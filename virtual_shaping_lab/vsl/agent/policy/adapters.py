"""Adapters between canonical policy grammar and runtime transport contracts.

Ownership policy (V3.20.0):
- Canonical policy composition spec lives in `vsl.agent.policy.spec.PolicySpec`
- Runtime transport policy config lives in `vsl.spec.contracts.PolicySpec`
"""

from __future__ import annotations

from typing import Any, Mapping

from virtual_shaping_lab.vsl.agent.policy.spec import PolicySpec as GrammarPolicySpec
from virtual_shaping_lab.vsl.spec.contracts import PolicySpec as RuntimePolicySpec


def grammar_to_runtime_policy_config(spec: GrammarPolicySpec) -> RuntimePolicySpec:
    """Adapt canonical grammar policy spec into runtime transport policy config."""
    if not isinstance(spec, GrammarPolicySpec):
        raise TypeError("spec must be GrammarPolicySpec.")

    params = {
        "selection_rule": spec.selection_rule,
        "action_space_mode": spec.action_space_mode,
        "tie_break_rule": spec.tie_break_rule,
        "availability_rule": spec.availability_rule,
        "parameters": dict(spec.parameters),
        "grammar_metadata": dict(spec.metadata),
    }
    return RuntimePolicySpec(name=spec.selection_rule, params=params)


def runtime_to_grammar_policy_spec(
    runtime_spec: RuntimePolicySpec,
    *,
    metadata: Mapping[str, Any] | None = None,
) -> GrammarPolicySpec:
    """Adapt runtime transport policy config back to canonical grammar policy spec."""
    if not isinstance(runtime_spec, RuntimePolicySpec):
        raise TypeError("runtime_spec must be RuntimePolicySpec.")

    params = dict(runtime_spec.params or {})
    selection_rule = str(params.get("selection_rule") or runtime_spec.name or "").strip()
    action_space_mode = str(params.get("action_space_mode") or "").strip()
    if not action_space_mode:
        action_space_mode = "classical_none" if selection_rule == "null" else "discrete"

    merged_meta = dict(metadata or {})
    grammar_meta = params.get("grammar_metadata")
    if isinstance(grammar_meta, Mapping):
        merged_meta.update(dict(grammar_meta))

    raw_parameters = params.get("parameters", {})
    if not isinstance(raw_parameters, Mapping):
        raw_parameters = {}

    tie_break_rule = params.get("tie_break_rule")
    availability_rule = params.get("availability_rule")

    return GrammarPolicySpec(
        selection_rule=selection_rule,
        action_space_mode=action_space_mode,
        parameters=dict(raw_parameters),
        tie_break_rule=tie_break_rule if isinstance(tie_break_rule, str) else None,
        availability_rule=availability_rule if isinstance(availability_rule, str) else None,
        metadata=merged_meta,
    )

