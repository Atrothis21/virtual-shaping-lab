"""Typed parameter objects for experiment composition."""

from experiment.parameters.types import (
    AttentionParams,
    AttentionMechanismParams,
    ContextParams,
    ContextMapParams,
    EpsilonGreedyPolicyParams,
    ExperimentParameters,
    LearnerParams,
    NullPolicyParams,
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
from experiment.parameters.pipeline import ParameterNormalizerPipeline, ParameterValidatorPipeline
from experiment.parameters.composer import ParameterComposer, parameters_to_dict
from experiment.parameters.ownership_guards import validate_composed_parameter_ownership

__all__ = [
    "AttentionParams",
    "AttentionMechanismParams",
    "ContextParams",
    "ContextMapParams",
    "EpsilonGreedyPolicyParams",
    "ExperimentParameters",
    "LearnerParams",
    "NullPolicyParams",
    "PredictionErrorRuleParams",
    "RepresentationParams",
    "RuntimeParams",
    "SalienceParams",
    "SalienceOperatorParams",
    "SimilarityParams",
    "SimilarityKernelParams",
    "SoftmaxPolicyParams",
    "TemporalBasisParams",
    "UnitParams",
    "ParameterNormalizerPipeline",
    "ParameterValidatorPipeline",
    "ParameterComposer",
    "parameters_to_dict",
    "validate_composed_parameter_ownership",
]
