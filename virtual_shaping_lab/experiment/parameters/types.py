"""Parameter domain types for typed experiment composition."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping

from experiment.domain.types import TrialTimeSpec


@dataclass(frozen=True)
class ContextParams:
    mode: str
    contexts: tuple[str, ...] = ()
    inference_enabled: bool = False


@dataclass(frozen=True)
class ContextMapParams:
    variant: str = "gated"
    contexts: tuple[str, ...] = ()
    inference_enabled: bool = False


@dataclass(frozen=True)
class SalienceParams:
    default: float = 1.0
    overrides: Mapping[str, float] = field(default_factory=dict)


@dataclass(frozen=True)
class SalienceOperatorParams:
    variant: str = "diagonal"
    default: float = 1.0
    overrides: Mapping[str, float] = field(default_factory=dict)


@dataclass(frozen=True)
class SimilarityParams:
    enabled: bool = False
    matrix: Mapping[str, Mapping[str, float]] = field(default_factory=dict)


@dataclass(frozen=True)
class SimilarityKernelParams:
    variant: str = "matrix"
    enabled: bool = False
    matrix: Mapping[str, Mapping[str, float]] = field(default_factory=dict)


@dataclass(frozen=True)
class TemporalBasisParams:
    enabled: bool = False
    variant: str = "identity"
    dimension: int = 0
    params: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class RepresentationParams:
    context: ContextParams
    salience: SalienceParams
    similarity: SimilarityParams
    context_map: ContextMapParams = field(default_factory=ContextMapParams)
    salience_operator: SalienceOperatorParams = field(default_factory=SalienceOperatorParams)
    similarity_kernel: SimilarityKernelParams = field(default_factory=SimilarityKernelParams)
    temporal_basis: TemporalBasisParams = field(default_factory=TemporalBasisParams)


@dataclass(frozen=True)
class AttentionParams:
    mode: str
    default: float = 1.0
    overrides: Mapping[str, float] = field(default_factory=dict)


@dataclass(frozen=True)
class AttentionMechanismParams:
    variant: str = "none"
    default: float = 1.0
    overrides: Mapping[str, float] = field(default_factory=dict)
    params: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class PredictionErrorRuleParams:
    variant: str = "rescorla_wagner"
    params: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class LearnerParams:
    algorithm: str
    alpha: float
    gamma: float | None
    attention: AttentionParams
    attention_mechanism: AttentionMechanismParams = field(default_factory=AttentionMechanismParams)
    prediction_error_rule: PredictionErrorRuleParams = field(default_factory=PredictionErrorRuleParams)


@dataclass(frozen=True)
class NullPolicyParams:
    name: str = "null"


@dataclass(frozen=True)
class EpsilonGreedyPolicyParams:
    name: str = "epsilon_greedy"
    epsilon: float = 0.1
    actions: tuple[str, ...] = ()


@dataclass(frozen=True)
class SoftmaxPolicyParams:
    name: str = "softmax"
    temperature: float = 1.0
    actions: tuple[str, ...] = ()


PolicyParams = NullPolicyParams | EpsilonGreedyPolicyParams | SoftmaxPolicyParams


@dataclass(frozen=True)
class RuntimeParams:
    seed: int | None = None
    update_mode: str = "trial"
    record_mode: str = "trial"
    strict_records: bool = False
    debug: bool = False


@dataclass(frozen=True)
class UnitParams:
    unit_key: str
    name: str
    context_id: str | None
    n_trials: int
    time: TrialTimeSpec
    contingency: Mapping[str, Any] = field(default_factory=dict)
    schedule_runtime: Mapping[str, Any] | None = None
    learning_gate: Mapping[str, Any] = field(default_factory=dict)
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ExperimentParameters:
    representation: RepresentationParams
    learner: LearnerParams
    policy: PolicyParams
    runtime: RuntimeParams
    units: tuple[UnitParams, ...] = ()

