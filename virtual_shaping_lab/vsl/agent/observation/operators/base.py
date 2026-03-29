"""Executable observation operator protocols and null optional operators."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Protocol, runtime_checkable


@runtime_checkable
class RepresentationOperator(Protocol):
    """Map raw stimulus payload into typed representation state."""

    def represent(
        self,
        *,
        raw_stimulus: Any,
        metadata: Mapping[str, Any] | None = None,
    ) -> Any: ...


@runtime_checkable
class ContextOperator(Protocol):
    """Apply context transformation to representation state."""

    def contextualize(
        self,
        *,
        representation: Any,
        context_state: Any = None,
        metadata: Mapping[str, Any] | None = None,
    ) -> Any: ...


@runtime_checkable
class GeneralizationOperator(Protocol):
    """Apply generalization transform after contextualization."""

    def generalize(
        self,
        *,
        contextual_state: Any,
        metadata: Mapping[str, Any] | None = None,
    ) -> Any: ...


@dataclass(frozen=True)
class NullContextOperator:
    """No-op context operator for optional `C` path."""

    axis: str = "C"
    variant: str = "null_context"

    def contextualize(
        self,
        *,
        representation: Any,
        context_state: Any = None,
        metadata: Mapping[str, Any] | None = None,
    ) -> Any:
        _ = context_state, metadata
        return representation


@dataclass(frozen=True)
class NullGeneralizationOperator:
    """No-op generalization operator for optional `G` path."""

    axis: str = "G"
    variant: str = "null_generalization"

    def generalize(
        self,
        *,
        contextual_state: Any,
        metadata: Mapping[str, Any] | None = None,
    ) -> Any:
        _ = metadata
        return contextual_state

