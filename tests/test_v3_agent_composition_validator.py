from __future__ import annotations

import pytest

from virtual_shaping_lab.vsl.agent import AgentSpec, AgentSpecValidationError


def _legal_agent_spec() -> AgentSpec:
    return AgentSpec(
        observation_spec={
            "representation": "identity",
            "context": "none",
            "generalization": "none",
        },
        learner_spec={
            "trace": "none",
            "predictor": "state_value",
            "error": "rw_error",
            "attention": "fixed",
            "updater": "delta_rule",
            "policy": "none",
        },
        policy_spec={
            "selection_rule": "null",
            "action_space_mode": "classical_none",
            "parameters": {},
        },
        protocol_action_space="classical_none",
    )


def test_v3_20_15_agent_spec_accepts_legal_tuple():
    spec = _legal_agent_spec()
    assert isinstance(spec.stable_hash(), str)
    assert len(spec.stable_hash()) == 64


def test_v3_20_15_agent_spec_rejects_learner_policy_prediction_kind_mismatch():
    with pytest.raises(AgentSpecValidationError, match="AGT_E_LEARNER_POLICY_OUTPUT_KIND_MISMATCH"):
        AgentSpec(
            observation_spec={
                "representation": "stimulus_vector",
                "context": "none",
                "generalization": "none",
            },
            learner_spec={
                "trace": "none",
                "predictor": "state_value",
                "error": "rw_error",
                "attention": "fixed",
                "updater": "delta_rule",
                "policy": "none",
            },
            policy_spec={
                "selection_rule": "greedy",
                "action_space_mode": "discrete",
                "parameters": {},
            },
            protocol_action_space="discrete",
        )


def test_v3_20_15_agent_spec_rejects_policy_protocol_action_space_mismatch():
    with pytest.raises(AgentSpecValidationError, match="AGT_E_POLICY_PROTOCOL_ACTION_SPACE_MISMATCH"):
        AgentSpec(
            observation_spec={
                "representation": "identity",
                "context": "none",
                "generalization": "none",
            },
            learner_spec={
                "trace": "none",
                "predictor": "state_value",
                "error": "rw_error",
                "attention": "fixed",
                "updater": "delta_rule",
                "policy": "none",
            },
            policy_spec={
                "selection_rule": "uniform_random",
                "action_space_mode": "discrete",
                "parameters": {},
            },
            protocol_action_space="classical_none",
        )
