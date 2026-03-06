"""Debug telemetry policy contracts for runtime record emission."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping


DEBUG_MODE_TRIAL = "trial"
DEBUG_MODE_TICK = "tick"
DEBUG_MODE_BOTH = "both"
DEBUG_MODES: tuple[str, ...] = (DEBUG_MODE_TRIAL, DEBUG_MODE_TICK, DEBUG_MODE_BOTH)


@dataclass(frozen=True)
class DebugTelemetryPolicy:
    """
    Runtime debug telemetry emission policy.

    Fields:
    - enabled: global debug on/off switch.
    - mode: emission target (`trial`, `tick`, `both`).
    - max_active_features: optional cap for `debug.active_features`.
    - sample_every_n_ticks: optional decimation cadence for tick debug records.
    """

    enabled: bool = False
    mode: str = DEBUG_MODE_TICK
    max_active_features: int | None = None
    sample_every_n_ticks: int | None = None

    def __post_init__(self) -> None:
        if self.mode not in DEBUG_MODES:
            raise ValueError(
                f"DebugTelemetryPolicy.mode must be one of {DEBUG_MODES}; got '{self.mode}'."
            )
        if self.max_active_features is not None and self.max_active_features <= 0:
            raise ValueError("DebugTelemetryPolicy.max_active_features must be > 0 when provided.")
        if self.sample_every_n_ticks is not None and self.sample_every_n_ticks <= 0:
            raise ValueError("DebugTelemetryPolicy.sample_every_n_ticks must be > 0 when provided.")


DEFAULT_DEBUG_POLICY = DebugTelemetryPolicy()


def resolve_debug_policy(
    runtime_settings: Mapping[str, Any] | None,
    *,
    fallback_debug_flag: bool = False,
) -> DebugTelemetryPolicy:
    """
    Build a DebugTelemetryPolicy from runtime settings.

    Expected optional runtime settings keys:
    - `debug` (bool)
    - `debug_mode` (`trial` | `tick` | `both`)
    - `debug_max_active_features` (int)
    - `debug_sample_every_n_ticks` (int)
    """
    settings = runtime_settings or {}
    enabled = bool(settings.get("debug", fallback_debug_flag))
    mode = str(settings.get("debug_mode", DEFAULT_DEBUG_POLICY.mode))

    max_active_features = settings.get("debug_max_active_features")
    if max_active_features is not None:
        max_active_features = int(max_active_features)

    sample_every_n_ticks = settings.get("debug_sample_every_n_ticks")
    if sample_every_n_ticks is not None:
        sample_every_n_ticks = int(sample_every_n_ticks)

    return DebugTelemetryPolicy(
        enabled=enabled,
        mode=mode,
        max_active_features=max_active_features,
        sample_every_n_ticks=sample_every_n_ticks,
    )

