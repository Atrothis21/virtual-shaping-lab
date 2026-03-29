"""Canonical runtime seam for observation execution."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Sequence

from virtual_shaping_lab.vsl.agent.observation import (
    ExecutableObservationPreset,
    ObservationStepResult,
    build_executable_observation_preset,
)


def _normalize_runtime_stimulus_payload(stimulus: Any) -> dict[str, float]:
    """
    Normalize runtime stimulus payloads into deterministic observation inputs.

    Runtime normalization rules:
    - mapping values that are sequences become one-hot feature presence by item
    - mapping scalar values become keyed numeric features when coercible
    - uncoercible mapping scalar values become keyed feature presence = 1.0
    - bare sequences become one-hot feature presence
    - bare scalar values become one feature keyed by string form
    """
    if stimulus is None:
        return {}
    if isinstance(stimulus, Mapping):
        out: dict[str, float] = {}
        for key, value in dict(stimulus).items():
            if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
                for item in value:
                    out[str(item)] = 1.0
                continue
            try:
                out[str(key)] = float(value)
            except (TypeError, ValueError):
                out[str(key)] = 1.0
        return out
    if isinstance(stimulus, Sequence) and not isinstance(stimulus, (str, bytes, bytearray)):
        return {str(item): 1.0 for item in stimulus}
    try:
        return {str(stimulus): float(stimulus)}
    except (TypeError, ValueError):
        return {str(stimulus): 1.0}


def _normalize_runtime_context_state(*, context_state: Any, stimulus: Any) -> Any:
    if context_state is not None:
        return context_state
    if isinstance(stimulus, Mapping):
        payload = dict(stimulus)
        for key in ("context", "context_state"):
            if key in payload:
                return payload.get(key)
    return None


@dataclass
class RuntimeObservationAdapter:
    """Runtime adapter that routes observation execution through one canonical bundle seam."""

    preset_name: str
    executable: ExecutableObservationPreset

    def step(
        self,
        *,
        stimulus: Any,
        context_state: Any = None,
        metadata: Mapping[str, Any] | None = None,
    ) -> ObservationStepResult:
        normalized_stimulus = _normalize_runtime_stimulus_payload(stimulus)
        normalized_context_state = _normalize_runtime_context_state(
            context_state=context_state,
            stimulus=stimulus,
        )
        runtime_metadata = {
            **dict(metadata or {}),
            "runtime_observation": {
                "preset_name": self.preset_name,
                "normalization": "runtime_stimulus_v1",
            },
        }
        return self.executable.bundle.step(
            raw_stimulus=normalized_stimulus,
            context_state=normalized_context_state,
            metadata=runtime_metadata,
        )


def build_runtime_observation_adapter(
    *,
    preset_name: str = "identity_observation",
    stimulus_universe: Sequence[str] = ("tone", "noise", "light"),
    context_tags: Sequence[str] = ("A", "B"),
    kernel_sigma: float = 1.0,
    conjunction_prefix: str = "cfg:",
) -> RuntimeObservationAdapter:
    executable = build_executable_observation_preset(
        preset_name,
        stimulus_universe=stimulus_universe,
        context_tags=context_tags,
        kernel_sigma=kernel_sigma,
        conjunction_prefix=conjunction_prefix,
    )
    return RuntimeObservationAdapter(
        preset_name=preset_name,
        executable=executable,
    )

