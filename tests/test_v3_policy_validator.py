from __future__ import annotations

import pytest

from virtual_shaping_lab.vsl.agent.policy import PolicySpec, PolicySpecValidationError
from virtual_shaping_lab.vsl.agent.policy.validation import validate_policy_spec


def _base_spec() -> PolicySpec:
    return PolicySpec(
        selection_rule="greedy",
        action_space_mode="discrete",
        parameters={},
        tie_break_rule="stable_lexicographic",
        availability_rule="environment_declared",
    )


def test_v3_policy_validator_accepts_valid_spec():
    validate_policy_spec(_base_spec())


def test_v3_policy_validator_rejects_unknown_selection_rule():
    with pytest.raises(PolicySpecValidationError, match="POL_E_UNKNOWN_SELECTION_RULE"):
        PolicySpec(selection_rule="unknown", action_space_mode="discrete")


def test_v3_policy_validator_rejects_unknown_action_space_mode():
    with pytest.raises(PolicySpecValidationError, match="POL_E_UNKNOWN_ACTION_SPACE_MODE"):
        PolicySpec(selection_rule="greedy", action_space_mode="unknown")


def test_v3_policy_validator_rejects_epsilon_without_parameter():
    with pytest.raises(PolicySpecValidationError, match="POL_E_MISSING_REQUIRED_PARAMETER"):
        PolicySpec(selection_rule="epsilon_greedy", action_space_mode="discrete", parameters={})


def test_v3_policy_validator_rejects_bad_temperature():
    with pytest.raises(PolicySpecValidationError, match="POL_E_INVALID_TEMPERATURE"):
        PolicySpec(selection_rule="softmax", action_space_mode="discrete", parameters={"temperature": 0.0})

