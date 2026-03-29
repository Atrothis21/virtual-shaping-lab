"""Executable learner operator protocols and null optional operators."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, MutableMapping, Protocol, runtime_checkable


@runtime_checkable
class PredictionOperator(Protocol):
    """Compute prediction from features and mutable predictor state."""

    def __call__(
        self,
        *,
        features: Mapping[str, float],
        state: MutableMapping[str, Any] | None = None,
    ) -> Any: ...


@runtime_checkable
class ErrorOperator(Protocol):
    """Compute prediction error from reward + prediction trajectory."""

    def __call__(
        self,
        *,
        reward: float,
        prediction: float,
        next_prediction: float | None = None,
        done: bool = False,
    ) -> float: ...


@runtime_checkable
class UpdateOperator(Protocol):
    """Own mutation of learner parameters/state from error signal."""

    def __call__(
        self,
        *,
        state: MutableMapping[str, Any],
        features: Mapping[str, float],
        error: float,
        step_size: float,
    ) -> MutableMapping[str, Any]: ...


@runtime_checkable
class AttentionOperator(Protocol):
    """Optional attention hook between error and update steps."""

    def apply(
        self,
        *,
        attention_state: MutableMapping[str, float] | None,
        features: Mapping[str, float],
        error: float,
    ) -> MutableMapping[str, float] | None: ...


@runtime_checkable
class EligibilityOperator(Protocol):
    """Optional eligibility/trace hook between error and update steps."""

    def apply(
        self,
        *,
        eligibility_state: MutableMapping[str, float] | None,
        features: Mapping[str, float],
        discount: float,
        trace_decay: float,
    ) -> MutableMapping[str, float] | None: ...


@dataclass(frozen=True)
class NullAttentionOperator:
    """No-op attention operator for optional `A` path."""

    slot: str = "A"
    variant: str = "null_attention"

    def apply(
        self,
        *,
        attention_state: MutableMapping[str, float] | None,
        features: Mapping[str, float],
        error: float,
    ) -> MutableMapping[str, float] | None:
        _ = features, error
        return attention_state


@dataclass(frozen=True)
class NullEligibilityOperator:
    """No-op eligibility operator for optional `E` path."""

    slot: str = "E"
    variant: str = "null_trace"

    def apply(
        self,
        *,
        eligibility_state: MutableMapping[str, float] | None,
        features: Mapping[str, float],
        discount: float,
        trace_decay: float,
    ) -> MutableMapping[str, float] | None:
        _ = features, discount, trace_decay
        return eligibility_state


# Backward-compatible alias with V3.18.0 naming.
NullTraceOperator = NullEligibilityOperator

