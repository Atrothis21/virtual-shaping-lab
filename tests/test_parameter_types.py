from dataclasses import FrozenInstanceError

import pytest

from experiment.domain.types import TrialTimeSpec
from experiment.parameters.types import (
    AttentionParams,
    AttentionMechanismParams,
    ContextParams,
    ContextMapParams,
    EpsilonGreedyPolicyParams,
    ExperimentParameters,
    LearnerParams,
    PredictionErrorRuleParams,
    RepresentationParams,
    RuntimeParams,
    SalienceParams,
    SalienceOperatorParams,
    SimilarityParams,
    SimilarityKernelParams,
    SoftmaxPolicyParams,
    TemporalBasisParams,
    UnitParams,
)


def _sample_params(policy):
    rep = RepresentationParams(
        context=ContextParams(mode="gated", contexts=("A", "B"), inference_enabled=True),
        salience=SalienceParams(default=1.0, overrides={"tone": 0.7}),
        similarity=SimilarityParams(enabled=True, matrix={"tone": {"tone": 1.0}}),
        context_map=ContextMapParams(variant="gated", contexts=("A", "B"), inference_enabled=True),
        salience_operator=SalienceOperatorParams(variant="diagonal", default=1.0, overrides={"tone": 0.7}),
        similarity_kernel=SimilarityKernelParams(variant="matrix", enabled=True, matrix={"tone": {"tone": 1.0}}),
        temporal_basis=TemporalBasisParams(enabled=True, variant="identity", dimension=1, params={}),
    )
    learner = LearnerParams(
        algorithm="rescorla_wagner",
        alpha=0.2,
        gamma=0.0,
        attention=AttentionParams(mode="static", default=1.0, overrides={"tone": 0.9}),
        attention_mechanism=AttentionMechanismParams(
            variant="static",
            default=1.0,
            overrides={"tone": 0.9},
            params={},
        ),
        prediction_error_rule=PredictionErrorRuleParams(variant="rescorla_wagner", params={}),
    )
    runtime = RuntimeParams(seed=7, update_mode="tick", record_mode="tick", strict_records=True)
    unit = UnitParams(
        unit_key="acquisition",
        name="Acquisition",
        context_id="A",
        n_trials=10,
        time=TrialTimeSpec(duration_s=1.0, dt_s=0.1),
        contingency={"us": 1.0},
        schedule_runtime=None,
        learning_gate={"enabled": True},
        metadata={"phase_index": 0},
    )
    return ExperimentParameters(
        representation=rep,
        learner=learner,
        policy=policy,
        runtime=runtime,
        units=(unit,),
    )


def test_parameter_types_smoke_with_epsilon_greedy_policy():
    params = _sample_params(EpsilonGreedyPolicyParams(epsilon=0.2, actions=("left", "right")))
    assert params.learner.algorithm == "rescorla_wagner"
    assert params.learner.prediction_error_rule.variant == "rescorla_wagner"
    assert params.runtime.update_mode == "tick"
    assert params.units[0].name == "Acquisition"
    assert params.policy.name == "epsilon_greedy"


def test_parameter_types_smoke_with_softmax_policy():
    params = _sample_params(SoftmaxPolicyParams(temperature=0.5, actions=("left", "right")))
    assert params.policy.name == "softmax"
    assert params.policy.temperature == 0.5


def test_parameter_dataclasses_are_frozen():
    params = _sample_params(EpsilonGreedyPolicyParams())
    with pytest.raises(FrozenInstanceError):
        params.runtime.seed = 123  # type: ignore[misc]
