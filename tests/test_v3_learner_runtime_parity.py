from __future__ import annotations

from itertools import product

from virtual_shaping_lab.vsl.agent.learning import (
    COMPATIBILITY_MATRIX,
    SLOT_REGISTRIES,
    LearnerSpec,
    build_executable_learner_preset,
    grammar_to_runtime_learner_config,
)
from virtual_shaping_lab.vsl.agent.learning.validation import LearnerSpecValidationError


def _runtime_accepts_tuple(trace: str, predictor: str, error: str, attention: str, updater: str, policy: str) -> bool:
    try:
        LearnerSpec(
            trace=trace,
            predictor=predictor,
            error=error,
            attention=attention,
            updater=updater,
            policy=policy,
            metadata={},
        )
        return True
    except LearnerSpecValidationError:
        return False


def _matrix_accepts_tuple(trace: str, predictor: str, error: str, attention: str, updater: str, policy: str) -> bool:
    if error not in COMPATIBILITY_MATRIX["predictor_to_error"].get(predictor, []):
        return False
    if policy not in COMPATIBILITY_MATRIX["predictor_to_policy"].get(predictor, []):
        return False
    if updater not in COMPATIBILITY_MATRIX["trace_to_updater"].get(trace, []):
        return False
    if updater not in COMPATIBILITY_MATRIX["attention_to_updater_strict"].get(attention, []):
        return False

    q_req = COMPATIBILITY_MATRIX["error_requires_q_predictor"]
    if error in q_req["errors"] and predictor not in q_req["allowed_predictors"]:
        return False

    action_req = COMPATIBILITY_MATRIX["error_requires_action_policy"]
    if error in action_req["errors"] and policy in action_req["forbidden_policy"]:
        return False

    expected = COMPATIBILITY_MATRIX["expected_sarsa_policy"]
    if error in expected["error"] and policy not in expected["allowed_policies"]:
        return False

    policy_none_guard = COMPATIBILITY_MATRIX["policy_none_incompatible_predictors"]
    if predictor in policy_none_guard["predictors"] and policy in policy_none_guard["policy"]:
        return False

    ac = COMPATIBILITY_MATRIX["actor_critic_required"]
    actor_critic_predictor = predictor == ac["predictor"][0]
    if actor_critic_predictor and (
        error != ac["error"][0]
        or updater != ac["updater"][0]
        or policy != ac["policy"][0]
    ):
        return False
    if updater == ac["updater"][0] and predictor != ac["predictor"][0]:
        return False

    return True


def test_v3_learner_runtime_acceptance_parity_matches_registry_matrix():
    traces = SLOT_REGISTRIES["trace"]
    predictors = SLOT_REGISTRIES["predictor"]
    errors = SLOT_REGISTRIES["error"]
    attentions = SLOT_REGISTRIES["attention"]
    updaters = SLOT_REGISTRIES["updater"]
    policies = SLOT_REGISTRIES["policy"]

    runtime_accepted = set()
    matrix_accepted = set()
    for trace, predictor, error, attention, updater, policy in product(
        traces,
        predictors,
        errors,
        attentions,
        updaters,
        policies,
    ):
        tpl = (trace, predictor, error, attention, updater, policy)
        if _runtime_accepts_tuple(*tpl):
            runtime_accepted.add(tpl)
        if _matrix_accepts_tuple(*tpl):
            matrix_accepted.add(tpl)

    assert runtime_accepted == matrix_accepted


def test_v3_18_5_executable_preset_runtime_rule_parity():
    rw = build_executable_learner_preset("rescorla_wagner")
    td0 = build_executable_learner_preset("td0", gamma=0.9)

    rw_runtime = grammar_to_runtime_learner_config(rw.learner_spec)
    td_runtime = grammar_to_runtime_learner_config(td0.learner_spec)

    assert rw_runtime.rule == "rescorla_wagner"
    assert td_runtime.rule == "td_value"

