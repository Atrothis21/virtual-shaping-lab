"""Canonical runtime seam for protocol execution."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, Sequence

from virtual_shaping_lab.vsl.protocol import (
    ExecutableProtocolPreset,
    ProtocolStepResult,
    build_executable_protocol_preset,
)


def _normalize_available_actions(value: Any) -> tuple[Any, ...]:
    if value is None:
        return ()
    if isinstance(value, tuple):
        return value
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return tuple(value)
    return (value,)


def _normalize_stimulus(value: Any) -> dict[str, float]:
    if value is None:
        return {}
    if isinstance(value, Mapping):
        out: dict[str, float] = {}
        for key, item in dict(value).items():
            try:
                out[str(key)] = float(item)
            except (TypeError, ValueError):
                out[str(key)] = 1.0
        return out
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return {str(item): 1.0 for item in value}
    try:
        return {str(value): float(value)}
    except (TypeError, ValueError):
        return {str(value): 1.0}


def _normalize_runtime_phase_payload(phase_payload: Mapping[str, Any] | None) -> dict[str, Any]:
    payload = dict(phase_payload or {})
    out: dict[str, Any] = {}

    raw_t = payload.get("t", payload.get("step_index", payload.get("trial_index", 0)))
    try:
        out["t"] = int(raw_t)
    except (TypeError, ValueError):
        out["t"] = 0

    raw_phase_step = payload.get("phase_step", payload.get("step_index", out["t"]))
    try:
        out["phase_step"] = int(raw_phase_step)
    except (TypeError, ValueError):
        out["phase_step"] = out["t"]

    raw_dt = payload.get("dt_s", payload.get("iti_s", 1.0))
    try:
        out["dt_s"] = float(raw_dt)
    except (TypeError, ValueError):
        out["dt_s"] = 1.0

    raw_elapsed = payload.get("elapsed_s", 0.0)
    try:
        out["elapsed_s"] = float(raw_elapsed)
    except (TypeError, ValueError):
        out["elapsed_s"] = 0.0

    raw_cumulative = payload.get("cumulative_reward", 0.0)
    try:
        out["cumulative_reward"] = float(raw_cumulative)
    except (TypeError, ValueError):
        out["cumulative_reward"] = 0.0

    context = payload.get("context_state", payload.get("context"))
    if context is not None:
        out["context"] = context

    raw_actions = payload.get("available_actions", payload.get("actions", payload.get("action_set")))
    out["available_actions"] = _normalize_available_actions(raw_actions)

    raw_stimulus = payload.get("stimulus", payload.get("stimuli", payload.get("observation")))
    out["stimulus"] = _normalize_stimulus(raw_stimulus)

    return out


@dataclass
class RuntimeProtocolAdapter:
    """Runtime adapter that routes protocol execution through one canonical bundle seam."""

    preset_name: str
    executable: ExecutableProtocolPreset
    _runtime_state: dict[str, Any] = field(default_factory=dict)

    def reset(self) -> None:
        self._runtime_state = {}
        self.executable.bundle.state.clear()

    def step(
        self,
        *,
        phase_payload: Mapping[str, Any] | None = None,
        action: Any = None,
        metadata: Mapping[str, Any] | None = None,
    ) -> ProtocolStepResult:
        normalized = _normalize_runtime_phase_payload(phase_payload)
        self._runtime_state.update(normalized)
        self.executable.bundle.state.update(self._runtime_state)

        runtime_metadata = {
            **dict(metadata or {}),
            "runtime_protocol": {
                "preset_name": self.preset_name,
                "normalization": "runtime_phase_payload_v1",
            },
        }
        result = self.executable.bundle.step(action=action, metadata=runtime_metadata)

        self._runtime_state["t"] = int(result.advance.t)
        self._runtime_state["phase_step"] = int(result.advance.phase_step)
        self._runtime_state["dt_s"] = float(result.advance.dt_s)
        self._runtime_state["done"] = bool(result.stop.should_stop or result.consequence.done)
        self._runtime_state["last_reward"] = float(result.consequence.reward)
        self._runtime_state["elapsed_s"] = float(self._runtime_state.get("elapsed_s", 0.0)) + float(result.advance.dt_s)
        self._runtime_state["cumulative_reward"] = float(self._runtime_state.get("cumulative_reward", 0.0)) + float(
            result.consequence.reward
        )
        return result


def build_runtime_protocol_adapter(
    *,
    preset_name: str = "acquisition_protocol",
    max_trials: int = 5,
    dt_s: float = 1.0,
    criterion_reward_threshold: float = 3.0,
) -> RuntimeProtocolAdapter:
    executable = build_executable_protocol_preset(
        preset_name,
        max_trials=max_trials,
        dt_s=dt_s,
        criterion_reward_threshold=criterion_reward_threshold,
    )
    return RuntimeProtocolAdapter(
        preset_name=preset_name,
        executable=executable,
    )
