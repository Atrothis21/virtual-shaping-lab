"""Runtime phase catalog surface.

This module provides the authoritative runtime phase catalog API while
temporarily delegating to the existing factory-owned registry during the
V2.12 migration.
"""

from __future__ import annotations

from typing import Any, Callable

from experiment.factories.phase_factory import (
    PHASE_REGISTRY,
    build_phase as _build_phase_from_factory,
    validate_phase as _validate_phase_from_factory,
)

PHASE_BUILDERS: dict[str, Callable[..., Any]] = PHASE_REGISTRY


def available_phases() -> list[str]:
    """Return deterministic list of runtime phase keys."""
    return sorted(PHASE_BUILDERS.keys())


def validate_phase_key(name: str) -> None:
    """Validate that a runtime phase key exists."""
    _validate_phase_from_factory(name)


def build_phase(name: str, *, agent: Any, stimuli: Any = None, **phase_params: Any) -> Any:
    """Build a runtime phase by key."""
    return _build_phase_from_factory(name, agent=agent, stimuli=stimuli, **phase_params)

