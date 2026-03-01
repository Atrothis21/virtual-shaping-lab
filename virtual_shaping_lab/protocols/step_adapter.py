"""Protocol step adapter for record and metadata shaping."""

from __future__ import annotations

from dataclasses import replace
from typing import Any

from experiment.runtime_records import finalize_record


class ProtocolStepAdapter:
    def __init__(self, protocol_name: str):
        self.protocol_name = protocol_name

    def adapt(
        self,
        *,
        step: Any,
        phase_name: str,
        phase_index: int,
        is_last_phase: bool,
        trial_index: int,
        n_trials: int,
        records_sink: list[dict[str, Any]],
    ):
        metadata = dict(getattr(step, "metadata", {}) or {})
        record = metadata.get("record")

        if isinstance(record, dict):
            record.setdefault("phase", phase_name)
            record.setdefault("protocol_name", self.protocol_name)
            record.setdefault("subphase", phase_index)
            record.setdefault("subphase_name", phase_name)
            record.setdefault("unit_path", f"{self.protocol_name}.{phase_name}")
            finalize_record(
                record,
                phase_name=record.get("phase"),
                protocol_phase_index=record.get("subphase"),
                protocol_phase_name=record.get("subphase_name"),
            )
            records_sink.append(record)
            metadata["record"] = record

        metadata.setdefault("protocol_name", self.protocol_name)
        metadata.setdefault("phase_name", phase_name)
        metadata.setdefault("unit_path", f"{self.protocol_name}.{phase_name}")

        done = bool(getattr(step, "done", False)) and (
            is_last_phase and trial_index + 1 >= n_trials
        )
        return replace(step, done=done, metadata=metadata)

