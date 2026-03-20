"""Learner-grammar legality validator for V3.5.0."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

TRACE_VALUES = {"none", "eligibility", "recency"}
PREDICTOR_VALUES = {"state_value", "q_value", "actor_critic_pair", "nonlinear_value", "nonlinear_q"}
ERROR_VALUES = {
    "rw_error",
    "td_error",
    "sarsa_error",
    "q_error",
    "expected_sarsa_error",
    "mc_error",
    "actor_critic_td_error",
}
ATTENTION_VALUES = {"fixed", "pearce_hall", "mackintosh", "hybrid_attention"}
UPDATER_VALUES = {"delta_rule", "trace_delta_rule", "attention_delta_rule", "gradient_rule", "actor_critic_update"}
POLICY_VALUES = {"none", "epsilon_greedy", "softmax", "greedy", "actor_policy"}

PREDICTOR_TO_ERRORS: dict[str, set[str]] = {
    "state_value": {"rw_error", "td_error", "mc_error"},
    "nonlinear_value": {"rw_error", "td_error", "mc_error"},
    "q_value": {"sarsa_error", "q_error", "expected_sarsa_error", "mc_error"},
    "nonlinear_q": {"sarsa_error", "q_error", "expected_sarsa_error", "mc_error"},
    "actor_critic_pair": {"actor_critic_td_error"},
}

PREDICTOR_TO_POLICIES: dict[str, set[str]] = {
    "state_value": {"none"},
    "nonlinear_value": {"none"},
    "q_value": {"epsilon_greedy", "softmax", "greedy"},
    "nonlinear_q": {"epsilon_greedy", "softmax", "greedy"},
    "actor_critic_pair": {"actor_policy"},
}

TRACE_TO_UPDATERS: dict[str, set[str]] = {
    "none": {"delta_rule", "attention_delta_rule", "gradient_rule", "actor_critic_update"},
    "eligibility": {"delta_rule", "trace_delta_rule", "attention_delta_rule", "gradient_rule", "actor_critic_update"},
    "recency": {"delta_rule", "trace_delta_rule", "attention_delta_rule", "gradient_rule"},
}

ATTENTION_TO_UPDATERS_STRICT: dict[str, set[str]] = {
    "fixed": {"delta_rule", "trace_delta_rule", "gradient_rule", "actor_critic_update"},
    "pearce_hall": {"attention_delta_rule", "gradient_rule"},
    "mackintosh": {"attention_delta_rule", "gradient_rule"},
    "hybrid_attention": {"attention_delta_rule", "gradient_rule"},
}


@dataclass(frozen=True)
class LearnerSpecValidationError(ValueError):
    code: str
    message: str

    def __str__(self) -> str:
        return f"[{self.code}] {self.message}"


def _reject(code: str, message: str) -> None:
    raise LearnerSpecValidationError(code=code, message=message)


def validate_learner_spec(spec: Any) -> None:
    """
    Validate learner tuple legality.

    Fail-fast and deterministic. Raises LearnerSpecValidationError.
    """

    trace = getattr(spec, "trace", None)
    predictor = getattr(spec, "predictor", None)
    error = getattr(spec, "error", None)
    attention = getattr(spec, "attention", None)
    updater = getattr(spec, "updater", None)
    policy = getattr(spec, "policy", None)

    if trace not in TRACE_VALUES:
        _reject("LGR_E_UNKNOWN_TRACE", f"Unsupported trace '{trace}'.")
    if predictor not in PREDICTOR_VALUES:
        _reject("LGR_E_UNKNOWN_PREDICTOR", f"Unsupported predictor '{predictor}'.")
    if error not in ERROR_VALUES:
        _reject("LGR_E_UNKNOWN_ERROR", f"Unsupported error '{error}'.")
    if attention not in ATTENTION_VALUES:
        _reject("LGR_E_UNKNOWN_ATTENTION", f"Unsupported attention '{attention}'.")
    if updater not in UPDATER_VALUES:
        _reject("LGR_E_UNKNOWN_UPDATER", f"Unsupported updater '{updater}'.")
    if policy not in POLICY_VALUES:
        _reject("LGR_E_UNKNOWN_POLICY", f"Unsupported policy '{policy}'.")

    if error in {"sarsa_error", "q_error", "expected_sarsa_error"} and predictor not in {"q_value", "nonlinear_q"}:
        _reject(
            "LGR_E_ERROR_REQUIRES_Q_PREDICTOR",
            f"Error '{error}' requires q-value predictor family.",
        )

    if updater == "actor_critic_update" and predictor != "actor_critic_pair":
        _reject(
            "LGR_E_ACTOR_CRITIC_UPDATER_REQUIRES_AC_PREDICTOR",
            "actor_critic_update requires predictor='actor_critic_pair'.",
        )

    if predictor == "actor_critic_pair":
        if error != "actor_critic_td_error":
            _reject("LGR_E_ACTOR_CRITIC_ERROR", "actor_critic_pair requires error='actor_critic_td_error'.")
        if updater != "actor_critic_update":
            _reject("LGR_E_ACTOR_CRITIC_UPDATER", "actor_critic_pair requires updater='actor_critic_update'.")
        if policy != "actor_policy":
            _reject("LGR_E_ACTOR_CRITIC_POLICY", "actor_critic_pair requires policy='actor_policy'.")

    if error in {"sarsa_error", "q_error"} and policy == "none":
        _reject("LGR_E_ERROR_REQUIRES_ACTION_POLICY", f"Error '{error}' requires non-null action policy.")

    if error == "expected_sarsa_error" and policy not in {"epsilon_greedy", "softmax"}:
        _reject(
            "LGR_E_EXPECTED_SARSA_POLICY",
            "expected_sarsa_error requires policy in {'epsilon_greedy', 'softmax'}.",
        )

    if updater == "trace_delta_rule" and trace == "none":
        _reject("LGR_E_TRACE_REQUIRED", "trace_delta_rule requires trace != 'none'.")

    if policy == "none" and predictor in {"q_value", "nonlinear_q", "actor_critic_pair"}:
        _reject("LGR_E_POLICY_NONE_INCOMPATIBLE", f"Policy 'none' is incompatible with predictor '{predictor}'.")

    if error not in PREDICTOR_TO_ERRORS[predictor]:
        _reject(
            "LGR_E_PREDICTOR_ERROR_MISMATCH",
            f"Predictor '{predictor}' is incompatible with error '{error}'.",
        )
    if policy not in PREDICTOR_TO_POLICIES[predictor]:
        _reject(
            "LGR_E_PREDICTOR_POLICY_MISMATCH",
            f"Predictor '{predictor}' is incompatible with policy '{policy}'.",
        )
    if updater not in TRACE_TO_UPDATERS[trace]:
        _reject(
            "LGR_E_TRACE_UPDATER_MISMATCH",
            f"Trace '{trace}' is incompatible with updater '{updater}'.",
        )
    if updater not in ATTENTION_TO_UPDATERS_STRICT[attention]:
        _reject(
            "LGR_E_ATTENTION_UPDATER_MISMATCH",
            f"Attention '{attention}' is incompatible with updater '{updater}' under strict semantics.",
        )
