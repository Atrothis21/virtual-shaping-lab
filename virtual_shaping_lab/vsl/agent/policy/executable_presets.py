"""Executable policy presets for V3.20.5 policy core."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from .operators import (
    EpsilonGreedyPolicy,
    GreedyActionSelectionPolicy,
    NullPolicyOperator,
    PolicyOperator,
    SoftmaxPolicy,
    UniformRandomPolicy,
)
from .spec import PolicySpec


@dataclass(frozen=True)
class ExecutablePolicyPreset:
    """Resolved executable policy preset payload."""

    preset_name: str
    policy_spec: PolicySpec
    policy_operator: PolicyOperator


def executable_policy_preset_names() -> list[str]:
    return ["no_policy", "greedy", "epsilon_greedy", "softmax", "uniform_random"]


def _coerce_policy_spec(spec: PolicySpec | Mapping[str, Any]) -> PolicySpec:
    if isinstance(spec, PolicySpec):
        return spec
    if isinstance(spec, Mapping):
        return PolicySpec.from_dict(dict(spec))
    raise TypeError("spec must be PolicySpec or object payload.")


def build_executable_policy_preset(
    preset_name: str,
    *,
    epsilon: float = 0.1,
    temperature: float = 1.0,
    tie_break_rule: str = "stable_lexicographic",
) -> ExecutablePolicyPreset:
    """Materialize executable policy operator presets."""
    requested = str(preset_name).strip()

    if requested == "no_policy":
        spec = PolicySpec(
            selection_rule="null",
            action_space_mode="classical_none",
            parameters={},
            tie_break_rule="stable_lexicographic",
            availability_rule="none",
            metadata={"preset_name": requested, "preset_version": "3.20.5"},
        )
        return ExecutablePolicyPreset(requested, spec, NullPolicyOperator())

    if requested == "greedy":
        spec = PolicySpec(
            selection_rule="greedy",
            action_space_mode="discrete",
            parameters={},
            tie_break_rule=tie_break_rule,
            availability_rule="environment_declared",
            metadata={"preset_name": requested, "preset_version": "3.20.5"},
        )
        return ExecutablePolicyPreset(requested, spec, GreedyActionSelectionPolicy(tie_break_rule=tie_break_rule))

    if requested == "epsilon_greedy":
        spec = PolicySpec(
            selection_rule="epsilon_greedy",
            action_space_mode="discrete",
            parameters={"epsilon": float(epsilon)},
            tie_break_rule="random",
            availability_rule="environment_declared",
            metadata={"preset_name": requested, "preset_version": "3.20.5"},
        )
        return ExecutablePolicyPreset(
            requested,
            spec,
            EpsilonGreedyPolicy(epsilon=float(epsilon), tie_break_rule="random"),
        )

    if requested == "softmax":
        spec = PolicySpec(
            selection_rule="softmax",
            action_space_mode="discrete",
            parameters={"temperature": float(temperature)},
            tie_break_rule="random",
            availability_rule="environment_declared",
            metadata={"preset_name": requested, "preset_version": "3.20.5"},
        )
        return ExecutablePolicyPreset(requested, spec, SoftmaxPolicy(temperature=float(temperature)))

    if requested == "uniform_random":
        spec = PolicySpec(
            selection_rule="uniform_random",
            action_space_mode="discrete",
            parameters={},
            tie_break_rule="random",
            availability_rule="environment_declared",
            metadata={"preset_name": requested, "preset_version": "3.20.5"},
        )
        return ExecutablePolicyPreset(requested, spec, UniformRandomPolicy())

    known = ", ".join(executable_policy_preset_names())
    raise ValueError(f"Unknown executable policy preset '{preset_name}'. Known presets: {known}")


def build_executable_policy_from_spec(
    spec: PolicySpec | Mapping[str, Any],
) -> ExecutablePolicyPreset:
    """Materialize executable policy operator directly from legal symbolic policy spec."""
    policy_spec = _coerce_policy_spec(spec)
    signature = policy_spec.selection_rule

    if signature == "null":
        return build_executable_policy_preset("no_policy")
    if signature == "greedy":
        return build_executable_policy_preset(
            "greedy",
            tie_break_rule=policy_spec.tie_break_rule or "stable_lexicographic",
        )
    if signature == "epsilon_greedy":
        epsilon = float(policy_spec.parameters.get("epsilon", 0.1))
        return build_executable_policy_preset("epsilon_greedy", epsilon=epsilon)
    if signature == "softmax":
        temperature = float(policy_spec.parameters.get("temperature", 1.0))
        return build_executable_policy_preset("softmax", temperature=temperature)
    if signature == "uniform_random":
        return build_executable_policy_preset("uniform_random")

    raise ValueError(
        "[POL_E_EXECUTABLE_UNSUPPORTED_SPEC] Symbolic policy spec is legal but does not map "
        "to a V3.20.5 executable core preset."
    )

