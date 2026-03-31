"""Policy instantiation boundary from grammar tuples to typed contracts.

V3.20.0 slice 4 scope:
- enforce policy legality before materialization
- expose deterministic typed boundary payload for runtime assembly
- provide machine-readable failure catalog and errors
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping

from .adapters import grammar_to_runtime_policy_config, runtime_to_grammar_policy_spec
from .spec import PolicySpec
from .validation import PolicySpecValidationError
from virtual_shaping_lab.vsl.spec.contracts import PolicySpec as RuntimePolicyConfig


POLICY_INSTANTIATION_FAILURES: dict[str, str] = {
    "INST_E_INVALID_SPEC_INPUT": "Policy spec input must be PolicySpec or object payload.",
    "INST_E_LEGALITY": "Policy spec failed legality validation before materialization.",
    "INST_E_BOUNDARY_RESOLUTION": "Policy boundary resolution failed for legacy/runtime inputs.",
}


@dataclass
class PolicyInstantiationError(ValueError):
    code: str
    message: str
    details: dict[str, Any] = field(default_factory=dict)

    def __str__(self) -> str:
        return f"[{self.code}] {self.message}"


@dataclass(frozen=True)
class PolicyOperatorHandle:
    slot: str
    variant: str
    params: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.slot, str) or not self.slot.strip():
            raise ValueError("PolicyOperatorHandle.slot must be a non-empty string.")
        if not isinstance(self.variant, str) or not self.variant.strip():
            raise ValueError("PolicyOperatorHandle.variant must be a non-empty string.")
        if not isinstance(self.params, dict):
            raise ValueError("PolicyOperatorHandle.params must be an object.")


@dataclass(frozen=True)
class PolicyInstantiationArtifact:
    policy_spec: PolicySpec
    runtime_config: RuntimePolicyConfig
    selection_operator: PolicyOperatorHandle
    action_space_mode: str


def _coerce_policy_spec(spec: PolicySpec | Mapping[str, Any]) -> PolicySpec:
    if isinstance(spec, PolicySpec):
        return spec
    if isinstance(spec, Mapping):
        try:
            return PolicySpec.from_dict(dict(spec))
        except (PolicySpecValidationError, ValueError, TypeError) as exc:
            raise PolicyInstantiationError(
                "INST_E_LEGALITY",
                POLICY_INSTANTIATION_FAILURES["INST_E_LEGALITY"],
                details={"reason": str(exc)},
            ) from exc
    raise PolicyInstantiationError(
        "INST_E_INVALID_SPEC_INPUT",
        POLICY_INSTANTIATION_FAILURES["INST_E_INVALID_SPEC_INPUT"],
    )


def instantiate_policy_contracts(spec: PolicySpec | Mapping[str, Any]) -> PolicyInstantiationArtifact:
    """Materialize typed policy boundary contracts from canonical grammar spec."""
    policy_spec = _coerce_policy_spec(spec)
    runtime_config = grammar_to_runtime_policy_config(policy_spec)
    return PolicyInstantiationArtifact(
        policy_spec=policy_spec,
        runtime_config=runtime_config,
        selection_operator=PolicyOperatorHandle(
            slot="Pi",
            variant=policy_spec.selection_rule,
            params=dict(policy_spec.parameters),
        ),
        action_space_mode=policy_spec.action_space_mode,
    )


def instantiate_policy_from_boundary(
    *,
    policy_rule: Any,
    policy_config: Mapping[str, Any] | None = None,
    metadata: Mapping[str, Any] | None = None,
) -> PolicyInstantiationArtifact:
    """Resolve boundary policy inputs and materialize typed policy contracts."""
    try:
        params = dict(policy_config or {})
        if "selection_rule" not in params:
            params["selection_rule"] = policy_rule
        if "parameters" not in params and isinstance(params.get("params"), Mapping):
            params["parameters"] = dict(params.get("params", {}))
        runtime_spec = RuntimePolicyConfig(name=str(policy_rule), params=params)
        resolved = runtime_to_grammar_policy_spec(runtime_spec, metadata=metadata)
    except Exception as exc:
        raise PolicyInstantiationError(
            "INST_E_BOUNDARY_RESOLUTION",
            POLICY_INSTANTIATION_FAILURES["INST_E_BOUNDARY_RESOLUTION"],
            details={"reason": str(exc)},
        ) from exc
    return instantiate_policy_contracts(resolved)

