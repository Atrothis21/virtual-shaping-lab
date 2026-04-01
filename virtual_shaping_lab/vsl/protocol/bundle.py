"""Executable protocol bundle orchestration (V3.21.5 slice 4)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, MutableMapping

from .operators import AdvanceOperator, ConsequenceOperator, EmissionOperator, StopOperator
from .output import AdvanceOutput, ConsequenceOutput, EmissionOutput, ProtocolStepResult, StopOutput


def _coerce_emission_output(value: Any) -> EmissionOutput:
    if isinstance(value, EmissionOutput):
        return value
    if isinstance(value, Mapping):
        return EmissionOutput(
            stimulus=dict(value.get("stimulus", {})),
            context=value.get("context"),
            available_actions=tuple(value.get("available_actions", ())),
            emission_state=dict(value.get("emission_state", {})),
            metadata=dict(value.get("metadata", {})),
        )
    raise ValueError("Emission operator must return EmissionOutput or mapping payload.")


def _coerce_consequence_output(value: Any) -> ConsequenceOutput:
    if isinstance(value, ConsequenceOutput):
        return value
    if isinstance(value, Mapping):
        return ConsequenceOutput(
            reward=float(value.get("reward", 0.0)),
            done=bool(value.get("done", False)),
            outcome_state=dict(value.get("outcome_state", {})),
            metadata=dict(value.get("metadata", {})),
        )
    raise ValueError("Consequence operator must return ConsequenceOutput or mapping payload.")


def _coerce_advance_output(value: Any) -> AdvanceOutput:
    if isinstance(value, AdvanceOutput):
        return value
    if isinstance(value, Mapping):
        return AdvanceOutput(
            t=int(value.get("t", 0)),
            dt_s=float(value.get("dt_s", 1.0)),
            phase_step=int(value.get("phase_step", 0)),
            advance_state=dict(value.get("advance_state", {})),
            metadata=dict(value.get("metadata", {})),
        )
    raise ValueError("Advance operator must return AdvanceOutput or mapping payload.")


def _coerce_stop_output(value: Any) -> StopOutput:
    if isinstance(value, StopOutput):
        return value
    if isinstance(value, Mapping):
        return StopOutput(
            should_stop=bool(value.get("should_stop", False)),
            reason=value.get("reason"),
            stop_state=dict(value.get("stop_state", {})),
            metadata=dict(value.get("metadata", {})),
        )
    raise ValueError("Stop operator must return StopOutput or mapping payload.")


@dataclass
class ProtocolBundle:
    """
    Canonical executable protocol order:
    1) emit
    2) consequence
    3) advance
    4) stop
    5) finalize typed ProtocolStepResult
    """

    emission_operator: EmissionOperator
    consequence_operator: ConsequenceOperator
    advance_operator: AdvanceOperator
    stop_operator: StopOperator
    state: MutableMapping[str, Any] = field(default_factory=dict)

    def step(
        self,
        *,
        action: Any = None,
        metadata: Mapping[str, Any] | None = None,
    ) -> ProtocolStepResult:
        incoming_metadata = dict(metadata or {})
        current_state = dict(self.state)

        emission_raw = self.emission_operator.emit(
            state=current_state,
            metadata=incoming_metadata,
        )
        emission = _coerce_emission_output(emission_raw)

        consequence_raw = self.consequence_operator.consequence(
            emission=emission,
            action=action,
            state=current_state,
            metadata=incoming_metadata,
        )
        consequence = _coerce_consequence_output(consequence_raw)

        advance_raw = self.advance_operator.advance(
            state=current_state,
            consequence=consequence,
            metadata=incoming_metadata,
        )
        advance = _coerce_advance_output(advance_raw)

        stop_raw = self.stop_operator.should_stop(
            state=current_state,
            advance=advance,
            consequence=consequence,
            metadata=incoming_metadata,
        )
        stop = _coerce_stop_output(stop_raw)

        self.state["t"] = int(advance.t)
        self.state["phase_step"] = int(advance.phase_step)
        self.state["dt_s"] = float(advance.dt_s)
        self.state["done"] = bool(stop.should_stop or consequence.done)
        self.state["last_reward"] = float(consequence.reward)

        stage_traces = {
            "emission": {
                "stimulus": dict(emission.stimulus),
                "context": emission.context,
                "available_actions": list(emission.available_actions),
                "metadata": dict(emission.metadata),
            },
            "consequence": {
                "reward": float(consequence.reward),
                "done": bool(consequence.done),
                "metadata": dict(consequence.metadata),
            },
            "advance": {
                "t": int(advance.t),
                "dt_s": float(advance.dt_s),
                "phase_step": int(advance.phase_step),
                "metadata": dict(advance.metadata),
            },
            "stop": {
                "should_stop": bool(stop.should_stop),
                "reason": stop.reason,
                "metadata": dict(stop.metadata),
            },
        }
        pipeline_order = ["emit", "consequence", "advance", "stop", "finalize"]
        merged_metadata = {
            **incoming_metadata,
            "stage_traces": stage_traces,
            "pipeline_order": pipeline_order,
        }

        return ProtocolStepResult(
            emission=emission,
            consequence=consequence,
            advance=advance,
            stop=stop,
            metadata=merged_metadata,
        )
