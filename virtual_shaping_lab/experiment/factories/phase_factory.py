"""Compatibility phase factory shim.

Authoritative phase construction now lives in
`experiment.phases.catalog_runtime`.
"""

from __future__ import annotations

import warnings
from typing import Any, Callable

from experiment.phases import catalog_runtime as _catalog_runtime

_WARNED = False


def _warn_deprecated_once() -> None:
    global _WARNED
    if _WARNED:
        return
    warnings.warn(
        "experiment.factories.phase_factory is a compatibility shim; use "
        "experiment.phases.catalog_runtime or experiment.phases.public.",
        DeprecationWarning,
        stacklevel=2,
    )
    _WARNED = True


# Kept for backward compatibility with existing imports/tests.
PHASE_REGISTRY: dict[str, Callable[..., Any]] = _catalog_runtime.PHASE_BUILDERS


def validate_phase(name: str) -> None:
    _warn_deprecated_once()
    if name not in PHASE_REGISTRY:
        available = ", ".join(sorted(PHASE_REGISTRY.keys()))
        raise KeyError(
            f"Unknown phase '{name}'. "
            f"Available phases: {available}"
        )


def build_phase(name: str, *, agent: Any, stimuli: Any = None, **phase_params: Any):
    _warn_deprecated_once()
    validate_phase(name)
    phase_cls = PHASE_REGISTRY[name]

    n_trials = phase_params.pop("n_trials", None)
    params = phase_params

    if stimuli is None:
        if n_trials is None:
            return phase_cls(agent=agent, params=params)
        return phase_cls(agent=agent, n_trials=n_trials, params=params)

    if n_trials is None:
        return phase_cls(agent=agent, stimuli=stimuli, params=params)
    return phase_cls(agent=agent, stimuli=stimuli, n_trials=n_trials, params=params)

