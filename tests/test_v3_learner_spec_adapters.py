from __future__ import annotations

from virtual_shaping_lab.vsl.agent.learning.adapters import (
    grammar_to_runtime_learner_config,
    runtime_to_grammar_learner_spec,
)
from virtual_shaping_lab.vsl.agent.learning.spec import LearnerSpec as GrammarLearnerSpec
from virtual_shaping_lab.vsl.spec.contracts import LearnerSpec as RuntimeLearnerSpec


def _rw_grammar() -> GrammarLearnerSpec:
    return GrammarLearnerSpec(
        trace="none",
        predictor="state_value",
        error="rw_error",
        attention="fixed",
        updater="delta_rule",
        policy="none",
        metadata={"preset_name": "rw"},
    )


def _q_grammar() -> GrammarLearnerSpec:
    return GrammarLearnerSpec(
        trace="none",
        predictor="q_value",
        error="q_error",
        attention="fixed",
        updater="delta_rule",
        policy="epsilon_greedy",
        metadata={"preset_name": "q_learning"},
    )


def test_grammar_to_runtime_transport_mapping_is_stable():
    runtime_cfg = grammar_to_runtime_learner_config(_rw_grammar(), attention_initial={"tone": 1.0})
    assert isinstance(runtime_cfg, RuntimeLearnerSpec)
    assert runtime_cfg.rule == "rescorla_wagner"
    assert runtime_cfg.params["trace"] == "none"
    assert runtime_cfg.params["predictor"] == "state_value"
    assert runtime_cfg.params["error"] == "rw_error"
    assert runtime_cfg.params["updater"] == "delta_rule"
    assert runtime_cfg.params["policy"] == "none"
    assert runtime_cfg.attention_config["name"] == "none"
    assert runtime_cfg.attention_initial == {"tone": 1.0}


def test_runtime_roundtrip_uses_embedded_grammar_tuple_when_present():
    original = _q_grammar()
    runtime_cfg = grammar_to_runtime_learner_config(original)
    rebuilt = runtime_to_grammar_learner_spec(runtime_cfg)
    assert rebuilt.to_dict() == original.to_dict()


def test_runtime_to_grammar_falls_back_to_legacy_resolution_when_tuple_absent():
    runtime_cfg = RuntimeLearnerSpec(
        rule="rescorla_wagner",
        params={},
        attention_initial={},
        attention_config={"name": "none", "params": {}},
    )
    rebuilt = runtime_to_grammar_learner_spec(runtime_cfg, metadata={"source": "fallback_test"})
    assert rebuilt.predictor == "state_value"
    assert rebuilt.error == "rw_error"
    assert rebuilt.policy == "none"
    assert rebuilt.metadata.get("source") == "fallback_test"

