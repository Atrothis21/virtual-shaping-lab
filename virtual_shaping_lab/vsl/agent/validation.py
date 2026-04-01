"""Compositional-agent legality validator for V3.20.15."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

PROTOCOL_ACTION_SPACE_VALUES = {"classical_none", "discrete", "binary_response"}
OBSERVATION_OUTPUT_KIND_BY_REPRESENTATION = {
    "identity": "symbolic_state",
    "stimulus_vector": "feature_vector",
    "temporal_basis": "feature_vector",
}
LEARNER_PREDICTOR_INPUT_KIND_REQUIREMENTS = {
    "state_value": {"symbolic_state", "feature_vector"},
    "q_value": {"symbolic_state", "feature_vector"},
    "nonlinear_value": {"feature_vector"},
    "nonlinear_q": {"feature_vector"},
    "actor_critic_pair": {"feature_vector"},
}
LEARNER_PREDICTOR_OUTPUT_KIND = {
    "state_value": "state_value",
    "nonlinear_value": "state_value",
    "q_value": "action_values",
    "nonlinear_q": "action_values",
    "actor_critic_pair": "action_values",
}
POLICY_SELECTION_REQUIRED_PREDICTION_KIND = {
    "null": "none",
    "uniform_random": "none",
    "greedy": "action_values",
    "epsilon_greedy": "action_values",
    "softmax": "action_values",
}


@dataclass
class AgentSpecValidationError(ValueError):
    code: str
    message: str

    def __str__(self) -> str:
        return f"[{self.code}] {self.message}"


def _reject(code: str, message: str) -> None:
    raise AgentSpecValidationError(code=code, message=message)


def validate_agent_spec(spec: Any) -> None:
    observation_spec = getattr(spec, "observation_spec", None)
    learner_spec = getattr(spec, "learner_spec", None)
    policy_spec = getattr(spec, "policy_spec", None)
    protocol_action_space = getattr(spec, "protocol_action_space", None)

    if protocol_action_space not in PROTOCOL_ACTION_SPACE_VALUES:
        _reject(
            "AGT_E_UNKNOWN_PROTOCOL_ACTION_SPACE",
            f"Unsupported protocol_action_space '{protocol_action_space}'.",
        )

    observation_representation = getattr(observation_spec, "representation", None)
    learner_predictor = getattr(learner_spec, "predictor", None)
    policy_selection_rule = getattr(policy_spec, "selection_rule", None)
    policy_action_space_mode = getattr(policy_spec, "action_space_mode", None)
    learner_policy = getattr(learner_spec, "policy", None)

    # Observation output shape vs learner predictor input requirements.
    observation_output_kind = OBSERVATION_OUTPUT_KIND_BY_REPRESENTATION.get(observation_representation)
    if observation_output_kind is None:
        _reject(
            "AGT_E_UNKNOWN_OBSERVATION_OUTPUT_KIND",
            f"Unsupported observation representation '{observation_representation}'.",
        )
    required_input_kinds = LEARNER_PREDICTOR_INPUT_KIND_REQUIREMENTS.get(learner_predictor)
    if required_input_kinds is None:
        _reject(
            "AGT_E_UNKNOWN_LEARNER_PREDICTOR",
            f"Unsupported learner predictor '{learner_predictor}'.",
        )
    if observation_output_kind not in required_input_kinds:
        allowed = ", ".join(sorted(required_input_kinds))
        _reject(
            "AGT_E_OBSERVATION_LEARNER_SHAPE_MISMATCH",
            f"Observation output kind '{observation_output_kind}' is incompatible with learner predictor "
            f"'{learner_predictor}'. Allowed kinds: {{{allowed}}}.",
        )

    # Learner output kind vs policy input requirements.
    learner_output_kind = LEARNER_PREDICTOR_OUTPUT_KIND.get(learner_predictor)
    required_prediction_kind = POLICY_SELECTION_REQUIRED_PREDICTION_KIND.get(policy_selection_rule)
    if required_prediction_kind is None:
        _reject(
            "AGT_E_UNKNOWN_POLICY_SELECTION_RULE",
            f"Unsupported policy selection_rule '{policy_selection_rule}'.",
        )
    if required_prediction_kind == "action_values" and learner_output_kind != "action_values":
        _reject(
            "AGT_E_LEARNER_POLICY_OUTPUT_KIND_MISMATCH",
            f"Policy selection_rule '{policy_selection_rule}' requires learner action-value output.",
        )

    # Policy action-space mode vs protocol action space compatibility.
    if policy_action_space_mode != protocol_action_space:
        _reject(
            "AGT_E_POLICY_PROTOCOL_ACTION_SPACE_MISMATCH",
            f"Policy action_space_mode '{policy_action_space_mode}' is incompatible with protocol_action_space "
            f"'{protocol_action_space}'.",
        )

    # NullPolicyOperator legality for classical presets.
    if policy_selection_rule == "null":
        if protocol_action_space != "classical_none":
            _reject(
                "AGT_E_NULL_POLICY_REQUIRES_CLASSICAL_PROTOCOL",
                "selection_rule='null' requires protocol_action_space='classical_none'.",
            )
        if learner_policy != "none":
            _reject(
                "AGT_E_NULL_POLICY_REQUIRES_LEARNER_NONE",
                "selection_rule='null' requires learner policy='none'.",
            )
    if protocol_action_space == "classical_none" and policy_selection_rule != "null":
        _reject(
            "AGT_E_CLASSICAL_PROTOCOL_REQUIRES_NULL_POLICY",
            "protocol_action_space='classical_none' requires policy selection_rule='null'.",
        )

