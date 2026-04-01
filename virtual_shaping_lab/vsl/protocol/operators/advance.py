"""Executable protocol advance operators."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from virtual_shaping_lab.vsl.protocol.output import AdvanceOutput, ConsequenceOutput


@dataclass(frozen=True)
class TrialAdvanceOperator:
    """Advance protocol state by one trial step."""

    dt_s: float = 1.0
    variant: str = "trial_increment"

    def __post_init__(self) -> None:
        object.__setattr__(self, "dt_s", float(self.dt_s))

    def advance(
        self,
        *,
        state: Mapping[str, Any],
        consequence: ConsequenceOutput,
        metadata: Mapping[str, Any] | None = None,
    ) -> AdvanceOutput:
        _ = consequence
        state_dict = dict(state)
        t_prev = int(state_dict.get("t", 0))
        phase_step_prev = int(state_dict.get("phase_step", t_prev))
        dt = float(state_dict.get("dt_s", self.dt_s))

        merged_meta = dict(metadata or {})
        merged_meta.setdefault("variant", self.variant)
        return AdvanceOutput(
            t=t_prev + 1,
            dt_s=dt,
            phase_step=phase_step_prev + 1,
            advance_state={"t_prev": t_prev, "phase_step_prev": phase_step_prev},
            metadata=merged_meta,
        )


@dataclass(frozen=True)
class EventAdvanceOperator:
    """Advance protocol event counter with configurable event-duration."""

    default_event_dt_s: float = 0.1
    variant: str = "event_increment"

    def __post_init__(self) -> None:
        object.__setattr__(self, "default_event_dt_s", float(self.default_event_dt_s))

    def advance(
        self,
        *,
        state: Mapping[str, Any],
        consequence: ConsequenceOutput,
        metadata: Mapping[str, Any] | None = None,
    ) -> AdvanceOutput:
        _ = consequence
        state_dict = dict(state)
        t_prev = int(state_dict.get("t", 0))
        phase_step_prev = int(state_dict.get("phase_step", t_prev))
        dt = float(state_dict.get("event_dt_s", self.default_event_dt_s))

        merged_meta = dict(metadata or {})
        merged_meta.setdefault("variant", self.variant)
        return AdvanceOutput(
            t=t_prev + 1,
            dt_s=dt,
            phase_step=phase_step_prev + 1,
            advance_state={"t_prev": t_prev, "phase_step_prev": phase_step_prev},
            metadata=merged_meta,
        )
