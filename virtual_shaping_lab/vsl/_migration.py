"""V3 namespace migration helpers for deprecation-window aliasing."""

from __future__ import annotations

import threading
import warnings
from contextlib import contextmanager

_STATE = threading.local()


def _suppressed() -> set[str]:
    current = getattr(_STATE, "suppressed", None)
    if current is None:
        current = set()
        _STATE.suppressed = current
    return current


@contextmanager
def suppress_deprecation_for(module_name: str):
    names = _suppressed()
    names.add(module_name)
    try:
        yield
    finally:
        names.discard(module_name)


def warn_deprecated_import(old_path: str, new_path: str, *, removal_release: str) -> None:
    if old_path in _suppressed():
        return
    warnings.warn(
        (
            f"Import path '{old_path}' is deprecated and will be removed in {removal_release}; "
            f"use '{new_path}' instead."
        ),
        DeprecationWarning,
        stacklevel=2,
    )
