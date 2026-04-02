"""Canonical runtime seam for post-run measurement execution."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from virtual_shaping_lab.vsl.measurement import (
    ExecutableMeasurementPreset,
    MeasurementStepResult,
    build_executable_measurement_preset,
)


def _normalize_runtime_measurement_records(records: list[Mapping[str, Any]]) -> list[dict[str, Any]]:
    """
    Normalize runtime measurement input records.

    Contract:
    - runtime measurement accepts post-run normalized rollout records only
    - each record must be mapping-like and will be shallow-copied into dict payload
    """
    if not isinstance(records, list):
        raise ValueError("Runtime measurement adapter requires a list of normalized rollout records.")
    normalized: list[dict[str, Any]] = []
    for idx, record in enumerate(records):
        if not isinstance(record, Mapping):
            raise ValueError(f"Runtime measurement record at index {idx} must be an object payload.")
        normalized.append(dict(record))
    return normalized


@dataclass
class RuntimeMeasurementAdapter:
    """Runtime adapter that routes post-run measurement through one canonical bundle seam."""

    preset_name: str
    executable: ExecutableMeasurementPreset

    def step(
        self,
        *,
        records: list[Mapping[str, Any]],
        metadata: Mapping[str, Any] | None = None,
    ) -> MeasurementStepResult:
        normalized_records = _normalize_runtime_measurement_records(records)
        runtime_metadata = {
            **dict(metadata or {}),
            "runtime_measurement": {
                "preset_name": self.preset_name,
                "normalization": "runtime_measurement_records_v1",
            },
        }
        return self.executable.bundle.step(
            records=normalized_records,
            metadata=runtime_metadata,
        )


def build_runtime_measurement_adapter(
    *,
    preset_name: str = "learning_curve_basic",
) -> RuntimeMeasurementAdapter:
    executable = build_executable_measurement_preset(preset_name)
    return RuntimeMeasurementAdapter(
        preset_name=preset_name,
        executable=executable,
    )
