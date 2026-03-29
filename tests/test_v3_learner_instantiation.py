from __future__ import annotations

import itertools

import pytest

from virtual_shaping_lab.vsl.agent.learning import (
    LEARNER_INSTANTIATION_FAILURES,
    LearnerSpec,
    LearnerSpecValidationError,
    LearnerInstantiationError,
    NullAttentionOperator,
    NullTraceOperator,
    expand_learner_preset,
    instantiate_learner_contracts,
    instantiate_learner_from_boundary,
    learner_preset_names,
    slot_registries,
)


def test_learner_instantiation_materializes_all_legal_presets():
    for preset_name in learner_preset_names():
        spec = expand_learner_preset(preset_name)
        artifact = instantiate_learner_contracts(spec)

        assert artifact.learner_spec.to_dict() == spec.to_dict()
        assert isinstance(artifact.runtime_config.rule, str) and artifact.runtime_config.rule
        assert artifact.predictor_operator.variant == spec.predictor
        assert artifact.error_operator.variant == spec.error
        assert artifact.updater_operator.variant == spec.updater
        assert artifact.policy_operator.variant == spec.policy

        if spec.attention == "fixed":
            assert isinstance(artifact.attention_operator, NullAttentionOperator)
        else:
            assert artifact.attention_operator.variant == spec.attention

        if spec.trace == "none":
            assert isinstance(artifact.trace_operator, NullTraceOperator)
        else:
            assert artifact.trace_operator.variant == spec.trace


def test_learner_instantiation_materializes_every_legal_tuple_from_registry_universe():
    regs = slot_registries()
    legal_count = 0
    for trace, predictor, error, attention, updater, policy in itertools.product(
        regs["trace"],
        regs["predictor"],
        regs["error"],
        regs["attention"],
        regs["updater"],
        regs["policy"],
    ):
        try:
            spec = LearnerSpec(
                trace=trace,
                predictor=predictor,
                error=error,
                attention=attention,
                updater=updater,
                policy=policy,
                metadata={"source": "registry_universe"},
            )
        except LearnerSpecValidationError:
            continue
        legal_count += 1
        artifact = instantiate_learner_contracts(spec)
        assert artifact.learner_spec.to_dict() == spec.to_dict()
        if spec.attention == "fixed":
            assert isinstance(artifact.attention_operator, NullAttentionOperator)
        else:
            assert artifact.attention_operator.variant == spec.attention
        if spec.trace == "none":
            assert isinstance(artifact.trace_operator, NullTraceOperator)
        else:
            assert artifact.trace_operator.variant == spec.trace

    assert legal_count > 0


def test_learner_instantiation_rejects_illegal_tuple_before_materialization():
    illegal = {
        "trace": "none",
        "predictor": "state_value",
        "error": "q_error",
        "attention": "fixed",
        "updater": "delta_rule",
        "policy": "none",
        "metadata": {"source": "test"},
    }
    with pytest.raises(LearnerInstantiationError, match="INST_E_LEGALITY"):
        instantiate_learner_contracts(illegal)


def test_learner_instantiation_boundary_resolves_legacy_input_and_materializes():
    artifact = instantiate_learner_from_boundary(
        learner_rule="rescorla_wagner",
        policy_config=None,
        learning_config={},
        metadata={"boundary": "test"},
    )
    assert artifact.learner_spec.predictor == "state_value"
    assert artifact.learner_spec.error == "rw_error"
    assert isinstance(artifact.attention_operator, NullAttentionOperator)
    assert isinstance(artifact.trace_operator, NullTraceOperator)


def test_learner_instantiation_failure_catalog_is_machine_readable():
    assert set(LEARNER_INSTANTIATION_FAILURES.keys()) == {
        "INST_E_INVALID_SPEC_INPUT",
        "INST_E_LEGALITY",
        "INST_E_BOUNDARY_RESOLUTION",
    }
