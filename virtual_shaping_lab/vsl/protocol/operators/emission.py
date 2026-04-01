"""Executable protocol emission operators."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping

from virtual_shaping_lab.vsl.protocol.output import EmissionOutput


def _normalize_stimulus(stimulus: Mapping[str, Any]) -> dict[str, float]:
    return {str(k): float(v) for k, v in dict(stimulus).items()}


@dataclass(frozen=True)
class FixedEmissionOperator:
    """Emit a fixed deterministic stimulus payload each step."""

    stimulus: dict[str, float] = field(default_factory=dict)
    context: str | None = None
    available_actions: tuple[Any, ...] = field(default_factory=tuple)
    emission_state: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)
    variant: str = "fixed_emission"

    def emit(
        self,
        *,
        state: Mapping[str, Any],
        metadata: Mapping[str, Any] | None = None,
    ) -> EmissionOutput:
        _ = state
        merged_meta = dict(self.metadata)
        merged_meta.update(dict(metadata or {}))
        merged_meta.setdefault("variant", self.variant)
        return EmissionOutput(
            stimulus=_normalize_stimulus(self.stimulus),
            context=self.context,
            available_actions=tuple(self.available_actions),
            emission_state=dict(self.emission_state),
            metadata=merged_meta,
        )


@dataclass(frozen=True)
class ScheduledEmissionOperator:
    """Emit from a deterministic schedule indexed by protocol time `t`."""

    schedule: tuple[dict[str, Any], ...]
    loop: bool = False
    variant: str = "scheduled_emission"

    def __post_init__(self) -> None:
        object.__setattr__(self, "schedule", tuple(self.schedule))
        if not self.schedule:
            raise ValueError("ScheduledEmissionOperator.schedule must be non-empty.")

    def emit(
        self,
        *,
        state: Mapping[str, Any],
        metadata: Mapping[str, Any] | None = None,
    ) -> EmissionOutput:
        raw_t = int(dict(state).get("t", 0))
        if self.loop:
            idx = raw_t % len(self.schedule)
        else:
            idx = max(0, min(raw_t, len(self.schedule) - 1))
        entry = dict(self.schedule[idx])
        merged_meta = dict(entry.get("metadata", {}))
        merged_meta.update(dict(metadata or {}))
        merged_meta.setdefault("variant", self.variant)
        return EmissionOutput(
            stimulus=_normalize_stimulus(dict(entry.get("stimulus", {}))),
            context=entry.get("context"),
            available_actions=tuple(entry.get("available_actions", ())),
            emission_state=dict(entry.get("emission_state", {})),
            metadata=merged_meta,
        )
