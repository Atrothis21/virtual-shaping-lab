"""Runtime hook callbacks for unit/trial/tick lifecycle events."""

from __future__ import annotations

from typing import Any


class RunnerHooks:
    """Optional observer callbacks for runtime lifecycle events."""

    def on_unit_start(self, *, unit: Any, ctx: Any) -> None:
        return None

    def on_unit_end(self, *, unit: Any, ctx: Any, records: list[dict[str, Any]]) -> None:
        return None

    def on_trial_start(self, *, unit: Any, ctx: Any, trial_id: Any, step: Any) -> None:
        return None

    def on_tick(
        self,
        *,
        unit: Any,
        ctx: Any,
        trial_id: Any,
        tick: int,
        observation: Any,
        action: Any,
        reward: float,
        metadata: dict[str, Any],
    ) -> None:
        return None

    def on_trial_end(self, *, unit: Any, ctx: Any, trial_id: Any, records: list[dict[str, Any]]) -> None:
        return None
