"""Deterministic replay harness over environment stepping."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Any

from virtual_shaping_lab.vsl.environment.contracts import IEnvironment
from virtual_shaping_lab.vsl.records import ROLLOUT_RECORD_SCHEMA_VERSION, RolloutRecord
from virtual_shaping_lab.vsl.rollout.records import step_to_rollout_record


def stable_rollout_hash(records: list[RolloutRecord]) -> str:
    """Compute a stable stream hash from ordered rollout records."""
    joined = "|".join(record.stable_hash() for record in records)
    return hashlib.sha256(joined.encode("utf-8")).hexdigest()


@dataclass
class ReplayHarness:
    """Deterministic replay harness that emits locked RolloutRecord objects."""

    max_steps: int | None = None
    schema_version: str = ROLLOUT_RECORD_SCHEMA_VERSION

    def run(
        self,
        environment: IEnvironment,
        *,
        rollout_id: str,
        episode_id: int = 0,
        seed: int | None = None,
        action: Any = None,
    ) -> list[RolloutRecord]:
        environment.reset(seed=seed)
        emitted: list[RolloutRecord] = []
        steps = 0
        while not environment.done:
            step = environment.step(action=action)
            emitted.append(
                step_to_rollout_record(
                    step,
                    schema_version=self.schema_version,
                    rollout_id=rollout_id,
                    episode_id=episode_id,
                )
            )
            steps += 1
            if self.max_steps is not None and steps >= self.max_steps:
                break
        return emitted

