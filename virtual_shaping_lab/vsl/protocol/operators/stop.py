"""Executable protocol stop operators."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from virtual_shaping_lab.vsl.protocol.output import AdvanceOutput, ConsequenceOutput, StopOutput


@dataclass(frozen=True)
class TrialCountStopOperator:
    """Stop when trial index reaches configured max trial count."""

    max_trials: int
    variant: str = "stop_on_trial_count"

    def __post_init__(self) -> None:
        object.__setattr__(self, "max_trials", int(self.max_trials))
        if self.max_trials < 1:
            raise ValueError("TrialCountStopOperator.max_trials must be >= 1.")

    def should_stop(
        self,
        *,
        state: Mapping[str, Any],
        advance: AdvanceOutput,
        consequence: ConsequenceOutput,
        metadata: Mapping[str, Any] | None = None,
    ) -> StopOutput:
        _ = state, consequence
        should = int(advance.t) >= self.max_trials
        merged_meta = dict(metadata or {})
        merged_meta.setdefault("variant", self.variant)
        return StopOutput(
            should_stop=should,
            reason="trial_count_reached" if should else None,
            stop_state={"max_trials": self.max_trials, "t": int(advance.t)},
            metadata=merged_meta,
        )


@dataclass(frozen=True)
class HorizonStopOperator:
    """Stop when protocol-owned elapsed time meets horizon."""

    horizon_s: float
    variant: str = "stop_on_horizon"

    def __post_init__(self) -> None:
        object.__setattr__(self, "horizon_s", float(self.horizon_s))
        if self.horizon_s <= 0.0:
            raise ValueError("HorizonStopOperator.horizon_s must be > 0.")

    def should_stop(
        self,
        *,
        state: Mapping[str, Any],
        advance: AdvanceOutput,
        consequence: ConsequenceOutput,
        metadata: Mapping[str, Any] | None = None,
    ) -> StopOutput:
        _ = consequence
        elapsed_s = float(dict(state).get("elapsed_s", 0.0)) + float(advance.dt_s)
        should = elapsed_s >= self.horizon_s
        merged_meta = dict(metadata or {})
        merged_meta.setdefault("variant", self.variant)
        return StopOutput(
            should_stop=should,
            reason="horizon_reached" if should else None,
            stop_state={"horizon_s": self.horizon_s, "elapsed_s": elapsed_s},
            metadata=merged_meta,
        )


@dataclass(frozen=True)
class CriterionStopOperator:
    """Stop when cumulative consequence reaches threshold criterion."""

    reward_threshold: float
    variant: str = "stop_on_criterion"

    def __post_init__(self) -> None:
        object.__setattr__(self, "reward_threshold", float(self.reward_threshold))

    def should_stop(
        self,
        *,
        state: Mapping[str, Any],
        advance: AdvanceOutput,
        consequence: ConsequenceOutput,
        metadata: Mapping[str, Any] | None = None,
    ) -> StopOutput:
        _ = advance
        cumulative_reward = float(dict(state).get("cumulative_reward", 0.0)) + float(consequence.reward)
        should = cumulative_reward >= self.reward_threshold
        merged_meta = dict(metadata or {})
        merged_meta.setdefault("variant", self.variant)
        return StopOutput(
            should_stop=should,
            reason="criterion_reached" if should else None,
            stop_state={
                "reward_threshold": self.reward_threshold,
                "cumulative_reward": cumulative_reward,
            },
            metadata=merged_meta,
        )
