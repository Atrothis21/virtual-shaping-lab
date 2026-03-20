"""Binding helpers for V3 temporal and episode runtime semantics."""

from __future__ import annotations

from typing import Any

from virtual_shaping_lab.vsl._migration import warn_deprecated_import
from virtual_shaping_lab.vsl.agent.representation import TemporalBasisSpec
from virtual_shaping_lab.vsl.environment import EpisodeSpec, HorizonSpec, TerminationCondition

warn_deprecated_import(
    "virtual_shaping_lab.vsl.spec.binding",
    "virtual_shaping_lab.vsl.spec.bindings",
    removal_release="V3.10.0",
)


def bind_temporal_basis_spec(representation: dict[str, Any]) -> TemporalBasisSpec:
    """Resolve representation temporal config into a typed TemporalBasisSpec."""
    params = representation.get("params") if isinstance(representation, dict) else None
    params = params if isinstance(params, dict) else {}
    raw_temporal = params.get("temporal_basis")
    if not isinstance(raw_temporal, dict):
        raw_temporal = {
            "variant": "identity",
            "dimension": 1,
            "enabled": False,
            "params": {},
        }
    return TemporalBasisSpec.from_dict(raw_temporal)


def bind_episode_spec(
    runtime: dict[str, Any],
    *,
    default_seed: int | None = None,
    default_rollout_id: str = "rollout_0",
    default_max_steps: int = 1,
) -> EpisodeSpec:
    """Resolve runtime episode/horizon config into typed episode contracts."""
    runtime = runtime if isinstance(runtime, dict) else {}
    raw_episode = runtime.get("episode") if isinstance(runtime.get("episode"), dict) else {}
    raw_horizon = raw_episode.get("horizon") if isinstance(raw_episode.get("horizon"), dict) else runtime.get("horizon")
    raw_horizon = raw_horizon if isinstance(raw_horizon, dict) else {}

    max_steps = raw_horizon.get("max_steps")
    max_duration_s = raw_horizon.get("max_duration_s")
    if max_steps is None and max_duration_s is None:
        max_steps = int(max(default_max_steps, 1))
    horizon = HorizonSpec(
        max_steps=max_steps,
        max_duration_s=max_duration_s,
        stop_reason=str(raw_horizon.get("stop_reason", "horizon_exhausted")),
    )

    raw_termination = raw_episode.get("termination") if isinstance(raw_episode.get("termination"), dict) else {}
    termination = TerminationCondition.from_dict(
        {
            "reason": raw_termination.get("reason", "running"),
            "terminal": bool(raw_termination.get("terminal", False)),
            "metadata": raw_termination.get("metadata", {}),
        }
    )

    seed = runtime.get("seed", default_seed)
    episode_id = raw_episode.get("episode_id", runtime.get("episode_id", 0))
    rollout_id = raw_episode.get("rollout_id", runtime.get("rollout_id", default_rollout_id))

    return EpisodeSpec(
        episode_id=int(episode_id),
        rollout_id=str(rollout_id),
        seed=(int(seed) if seed is not None else None),
        horizon=horizon,
        termination=termination,
    )

