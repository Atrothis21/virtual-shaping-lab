"""Executable eligibility/trace operators and lifecycle helpers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, MutableMapping

from .base import EligibilityOperator, NullEligibilityOperator


def _coerce_features(features: Mapping[str, float]) -> dict[str, float]:
    return {str(key): float(value) for key, value in features.items()}


def _coerce_state(eligibility_state: MutableMapping[str, float] | None) -> dict[str, float]:
    if not isinstance(eligibility_state, Mapping):
        return {}
    return {str(key): float(value) for key, value in eligibility_state.items()}


def reset_eligibility_state(
    eligibility_state: MutableMapping[str, float] | None = None,
) -> dict[str, float]:
    """
    Lifecycle reset helper.

    Semantics:
    - init: pass `None` to operator `apply(...)` and state initializes lazily.
    - carry-over: pass previous dict back into next `apply(...)`.
    - reset: call this helper to clear trace memory between episodes.
    """
    _ = eligibility_state
    return {}


@dataclass(frozen=True)
class AccumulatingEligibilityTraceOperator(EligibilityOperator):
    """Accumulating eligibility: e <- gamma*lambda*e + x."""

    slot: str = "E"
    variant: str = "accumulating_trace"

    def apply(
        self,
        *,
        eligibility_state: MutableMapping[str, float] | None,
        features: Mapping[str, float],
        discount: float,
        trace_decay: float,
    ) -> MutableMapping[str, float] | None:
        state = _coerce_state(eligibility_state)
        x = _coerce_features(features)
        coeff = float(discount) * float(trace_decay)
        for key, value in x.items():
            state[key] = coeff * float(state.get(key, 0.0)) + float(value)
        return state


@dataclass(frozen=True)
class ReplacingEligibilityTraceOperator(EligibilityOperator):
    """Replacing eligibility: active features set trace to 1 after decay step."""

    slot: str = "E"
    variant: str = "replacing_trace"

    def apply(
        self,
        *,
        eligibility_state: MutableMapping[str, float] | None,
        features: Mapping[str, float],
        discount: float,
        trace_decay: float,
    ) -> MutableMapping[str, float] | None:
        state = _coerce_state(eligibility_state)
        x = _coerce_features(features)
        coeff = float(discount) * float(trace_decay)
        for key in list(state.keys()):
            state[key] = coeff * float(state.get(key, 0.0))
        for key, value in x.items():
            if float(value) != 0.0:
                state[key] = 1.0
        return state


__all__ = [
    "NullEligibilityOperator",
    "AccumulatingEligibilityTraceOperator",
    "ReplacingEligibilityTraceOperator",
    "reset_eligibility_state",
]

