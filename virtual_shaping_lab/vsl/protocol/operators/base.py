"""Executable protocol operator protocols for V3.21.5."""

from __future__ import annotations

from typing import Any, Mapping, Protocol, runtime_checkable

from virtual_shaping_lab.vsl.protocol.output import (
    AdvanceOutput,
    ConsequenceOutput,
    EmissionOutput,
    StopOutput,
)


@runtime_checkable
class EmissionOperator(Protocol):
    """Emit protocol-visible stimulus/context/action availability."""

    def emit(
        self,
        *,
        state: Mapping[str, Any],
        metadata: Mapping[str, Any] | None = None,
    ) -> EmissionOutput: ...


@runtime_checkable
class ConsequenceOperator(Protocol):
    """Compute environment-side consequence from action and emitted state."""

    def consequence(
        self,
        *,
        emission: EmissionOutput,
        action: Any,
        state: Mapping[str, Any],
        metadata: Mapping[str, Any] | None = None,
    ) -> ConsequenceOutput: ...


@runtime_checkable
class AdvanceOperator(Protocol):
    """Advance protocol-owned temporal progression."""

    def advance(
        self,
        *,
        state: Mapping[str, Any],
        consequence: ConsequenceOutput,
        metadata: Mapping[str, Any] | None = None,
    ) -> AdvanceOutput: ...


@runtime_checkable
class StopOperator(Protocol):
    """Evaluate protocol-owned stop condition."""

    def should_stop(
        self,
        *,
        state: Mapping[str, Any],
        advance: AdvanceOutput,
        consequence: ConsequenceOutput,
        metadata: Mapping[str, Any] | None = None,
    ) -> StopOutput: ...
