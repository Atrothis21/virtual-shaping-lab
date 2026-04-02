"""Deterministic replay harness over environment stepping."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Any

from virtual_shaping_lab.vsl.environment.contracts import IEnvironment
from virtual_shaping_lab.vsl.measurement import MeasurementStepResult
from virtual_shaping_lab.vsl.records import ROLLOUT_RECORD_SCHEMA_VERSION, RolloutRecord
from virtual_shaping_lab.vsl.records.adapters.rollout_records import step_to_rollout_record
from virtual_shaping_lab.vsl.runtime.measurement_adapter import (
    RuntimeMeasurementAdapter,
    build_runtime_measurement_adapter,
)


def stable_rollout_hash(records: list[RolloutRecord]) -> str:
    """Compute a stable stream hash from ordered rollout records."""
    joined = "|".join(record.stable_hash() for record in records)
    return hashlib.sha256(joined.encode("utf-8")).hexdigest()


@dataclass
class ReplayHarness:
    """Deterministic replay harness that emits locked RolloutRecord objects."""

    max_steps: int | None = None
    schema_version: str = ROLLOUT_RECORD_SCHEMA_VERSION

    @staticmethod
    def _records_to_runtime_measurement_payload(records: list[RolloutRecord]) -> list[dict[str, Any]]:
        normalized: list[dict[str, Any]] = []
        for record in records:
            state = dict(record.trial_state or {})
            normalized.append(
                {
                    "trial_index": int(record.trial_index),
                    "reward": float(record.reward),
                    "action": record.action,
                    "task_input": {
                        "stimuli": dict(record.stimulus),
                        "available_actions": list(state.get("a", []))
                        if isinstance(state.get("a"), list)
                        else [],
                    },
                    "metadata": dict(record.metadata),
                }
            )
        return normalized

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

    def run_with_measurement(
        self,
        environment: IEnvironment,
        *,
        rollout_id: str,
        episode_id: int = 0,
        seed: int | None = None,
        action: Any = None,
        measurement_preset_name: str = "learning_curve_basic",
        measurement_adapter: RuntimeMeasurementAdapter | None = None,
        measurement_metadata: dict[str, Any] | None = None,
    ) -> tuple[list[RolloutRecord], MeasurementStepResult]:
        records = self.run(
            environment,
            rollout_id=rollout_id,
            episode_id=episode_id,
            seed=seed,
            action=action,
        )
        adapter = measurement_adapter or build_runtime_measurement_adapter(
            preset_name=measurement_preset_name
        )
        measurement_result = adapter.step(
            records=self._records_to_runtime_measurement_payload(records),
            metadata=dict(measurement_metadata or {}),
        )
        return records, measurement_result

