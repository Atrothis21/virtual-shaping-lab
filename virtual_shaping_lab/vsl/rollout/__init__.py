"""V3 rollout namespace."""

from __future__ import annotations

from importlib import import_module
from typing import Any

__all__ = [
    "step_to_rollout_record",
    "rollout_records_to_dict",
    "ReplayHarness",
    "stable_rollout_hash",
]


def __getattr__(name: str) -> Any:
    if name in {"step_to_rollout_record", "rollout_records_to_dict"}:
        mod = import_module("virtual_shaping_lab.vsl.records.adapters.rollout_records")
        return getattr(mod, name)
    if name in {"ReplayHarness", "stable_rollout_hash"}:
        mod = import_module("virtual_shaping_lab.vsl.rollout.replay_harness")
        return getattr(mod, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
