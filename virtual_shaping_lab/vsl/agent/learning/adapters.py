"""Adapters between canonical learner grammar and runtime transport contracts.

Ownership policy (V3.18.0):
- Canonical learner composition spec lives in `vsl.agent.learning.spec.LearnerSpec`
- Runtime transport learner config lives in `vsl.spec.contracts.LearnerSpec`
"""

from __future__ import annotations

from typing import Any, Mapping

from virtual_shaping_lab.vsl.agent.learning.resolve import resolve_learner_spec
from virtual_shaping_lab.vsl.agent.learning.spec import LearnerSpec as GrammarLearnerSpec
from virtual_shaping_lab.vsl.spec.contracts import LearnerSpec as RuntimeLearnerSpec

_GRAMMAR_TO_RUNTIME_ATTENTION_NAME = {
    "fixed": "none",
    "pearce_hall": "pearce_hall",
    "mackintosh": "mackintosh",
    "hybrid_attention": "mackintosh",
}


def _runtime_rule_from_grammar(spec: GrammarLearnerSpec) -> str:
    if spec.predictor in {"q_value", "nonlinear_q", "actor_critic_pair"} or spec.policy != "none":
        return "q_learner"
    if spec.error in {"td_error", "expected_sarsa_error"} or spec.updater == "trace_delta_rule":
        return "td_value"
    return "rescorla_wagner"


def grammar_to_runtime_learner_config(
    spec: GrammarLearnerSpec,
    *,
    attention_initial: Mapping[str, Any] | None = None,
) -> RuntimeLearnerSpec:
    """Adapt canonical grammar learner spec into runtime transport learner config."""
    if not isinstance(spec, GrammarLearnerSpec):
        raise TypeError("spec must be GrammarLearnerSpec.")

    attention_name = _GRAMMAR_TO_RUNTIME_ATTENTION_NAME.get(spec.attention, "none")
    params = {
        "trace": spec.trace,
        "predictor": spec.predictor,
        "error": spec.error,
        "attention": spec.attention,
        "updater": spec.updater,
        "policy": spec.policy,
        "grammar_metadata": dict(spec.metadata),
    }
    return RuntimeLearnerSpec(
        rule=_runtime_rule_from_grammar(spec),
        params=params,
        attention_initial=dict(attention_initial or {}),
        attention_config={"name": attention_name, "params": {}},
    )


def runtime_to_grammar_learner_spec(
    runtime_spec: RuntimeLearnerSpec,
    *,
    metadata: Mapping[str, Any] | None = None,
) -> GrammarLearnerSpec:
    """Adapt runtime transport learner config back to canonical grammar learner spec."""
    if not isinstance(runtime_spec, RuntimeLearnerSpec):
        raise TypeError("runtime_spec must be RuntimeLearnerSpec.")

    params = dict(runtime_spec.params or {})
    required = ("trace", "predictor", "error", "attention", "updater", "policy")
    if all(isinstance(params.get(key), str) and str(params.get(key)).strip() for key in required):
        merged_meta = dict(metadata or {})
        grammar_meta = params.get("grammar_metadata")
        if isinstance(grammar_meta, Mapping):
            merged_meta.update(dict(grammar_meta))
        return GrammarLearnerSpec(
            trace=str(params["trace"]),
            predictor=str(params["predictor"]),
            error=str(params["error"]),
            attention=str(params["attention"]),
            updater=str(params["updater"]),
            policy=str(params["policy"]),
            metadata=merged_meta,
        )

    learning_config = {
        "attention": {
            "config": runtime_spec.attention_config,
            "initial": runtime_spec.attention_initial,
        }
    }
    resolved = resolve_learner_spec(
        learner_rule=runtime_spec.rule,
        policy_config={"name": params.get("policy", "none")},
        learning_config=learning_config,
        metadata=dict(metadata or {}),
    )
    return resolved

