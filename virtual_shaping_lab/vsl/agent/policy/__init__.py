"""V3 policy primitives."""

from .action_space import ActionSpace, NullActionSpace, SingletonActionSpace
from .adapters import grammar_to_runtime_policy_config, runtime_to_grammar_policy_spec
from .instantiate import (
    POLICY_INSTANTIATION_FAILURES,
    PolicyInstantiationArtifact,
    PolicyInstantiationError,
    PolicyOperatorHandle,
    instantiate_policy_contracts,
    instantiate_policy_from_boundary,
)
from .input import PolicyInput, build_policy_input
from .executable_presets import (
    ExecutablePolicyPreset,
    build_executable_policy_from_spec,
    build_executable_policy_preset,
    executable_policy_preset_names,
)
from .null_policy import NullPolicy
from .operators import (
    ActionAvailabilityOperator,
    EpsilonGreedyPolicy,
    GreedyActionSelectionPolicy,
    NullPolicyOperator,
    PolicyOperator,
    PolicyOutput,
    SoftmaxPolicy,
    UniformRandomPolicy,
)
from .presets import (
    POLICY_PRESET_ALIASES,
    POLICY_PRESET_FAMILIES,
    POLICY_PRESETS,
    PRESET_VERSION,
    expand_policy_preset,
    policy_preset_aliases,
    policy_preset_families,
    policy_preset_hash,
    policy_preset_names,
    policy_preset_payload,
    policy_preset_registry,
)
from .registry import (
    COMPATIBILITY_MATRIX,
    POLICY_REGISTRY_VERSION,
    SLOT_REGISTRIES,
    compatibility_matrix,
    policy_registry_hash,
    policy_registry_payload,
    slot_registries,
)
from .spec import PolicySpec
from .validation import PolicySpecValidationError, validate_policy_spec

__all__ = [
    "ActionSpace",
    "NullActionSpace",
    "SingletonActionSpace",
    "NullPolicy",
    "ExecutablePolicyPreset",
    "build_executable_policy_preset",
    "build_executable_policy_from_spec",
    "executable_policy_preset_names",
    "PolicyInput",
    "build_policy_input",
    "PolicyOperator",
    "ActionAvailabilityOperator",
    "NullPolicyOperator",
    "PolicyOutput",
    "GreedyActionSelectionPolicy",
    "EpsilonGreedyPolicy",
    "SoftmaxPolicy",
    "UniformRandomPolicy",
    "grammar_to_runtime_policy_config",
    "runtime_to_grammar_policy_spec",
    "PolicyOperatorHandle",
    "PolicyInstantiationArtifact",
    "PolicyInstantiationError",
    "POLICY_INSTANTIATION_FAILURES",
    "instantiate_policy_contracts",
    "instantiate_policy_from_boundary",
    "PolicySpec",
    "PolicySpecValidationError",
    "validate_policy_spec",
    "POLICY_REGISTRY_VERSION",
    "SLOT_REGISTRIES",
    "COMPATIBILITY_MATRIX",
    "slot_registries",
    "compatibility_matrix",
    "policy_registry_payload",
    "policy_registry_hash",
    "PRESET_VERSION",
    "POLICY_PRESETS",
    "POLICY_PRESET_ALIASES",
    "POLICY_PRESET_FAMILIES",
    "policy_preset_names",
    "policy_preset_aliases",
    "policy_preset_registry",
    "policy_preset_families",
    "expand_policy_preset",
    "policy_preset_payload",
    "policy_preset_hash",
]

