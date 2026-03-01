"""Record finalization pipeline for stable TrialRecord boundaries."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Protocol

from experiment.domain.types import TrialRecord


_TRIAL_RECORD_DEFAULTS: dict[str, Any] = {
    "phase": None,
    "phase_name": None,
    "protocol_name": None,
    "unit_path": None,
    "subphase": None,
    "subphase_name": None,
    "trial": None,
    "tick": None,
    "t_s": None,
    "dt_s": None,
    "trial_step": None,
    "trial_id": None,
    "context": None,
    "stimulus": None,
    "stimulus_type": None,
    "action": None,
    "response": None,
    "reward": None,
    "prediction": None,
    "outcome_type": None,
    "schedule": None,
    "done": None,
    "learning_enabled": None,
    "metadata": {},
}


@dataclass(frozen=True)
class FinalizationContext:
    phase_name: str | None = None
    protocol_phase_index: int | None = None
    protocol_phase_name: str | None = None
    strict_mode: bool = False
    from_version: str = "v1"
    to_version: str = "v1"


class RecordNormalizer(Protocol):
    def apply(self, record: Dict[str, Any], ctx: FinalizationContext) -> None:
        ...


class SchemaDefaultsNormalizer:
    def apply(self, record: Dict[str, Any], ctx: FinalizationContext) -> None:
        for key, default in _TRIAL_RECORD_DEFAULTS.items():
            if key not in record:
                record[key] = {} if key == "metadata" else default


class ProtocolMetadataNormalizer:
    def apply(self, record: Dict[str, Any], ctx: FinalizationContext) -> None:
        if ctx.phase_name:
            if record.get("phase_name") is None:
                record["phase_name"] = ctx.phase_name
            if record.get("phase") is None:
                record["phase"] = ctx.phase_name
        if ctx.protocol_phase_index is not None:
            if record.get("subphase") is None:
                record["subphase"] = ctx.protocol_phase_index
        if ctx.protocol_phase_name:
            if record.get("subphase_name") is None:
                record["subphase_name"] = ctx.protocol_phase_name


class StrictModeValidator:
    """
    Optional strict validator for record invariants.

    Enabled only when FinalizationContext.strict_mode is True.
    """

    def apply(self, record: Dict[str, Any], ctx: FinalizationContext) -> None:
        if not ctx.strict_mode:
            return

        tick = record.get("tick")
        t_s = record.get("t_s")
        dt_s = record.get("dt_s")
        trial_step = record.get("trial_step")

        # Tick records must include time/grid fields.
        if tick is not None:
            if t_s is None:
                raise ValueError("Strict mode: tick record requires t_s.")
            if dt_s is None:
                raise ValueError("Strict mode: tick record requires dt_s.")
            if trial_step is None:
                raise ValueError("Strict mode: tick record requires trial_step.")

        # Monotonic check for contexts that provide previous tick info.
        metadata = record.get("metadata")
        if isinstance(metadata, dict):
            prev_tick = metadata.get("prev_tick")
            prev_t_s = metadata.get("prev_t_s")
            if prev_tick is not None and tick is not None and int(tick) < int(prev_tick):
                raise ValueError("Strict mode: tick must be monotonic non-decreasing.")
            if prev_t_s is not None and t_s is not None and float(t_s) < float(prev_t_s):
                raise ValueError("Strict mode: t_s must be monotonic non-decreasing.")


class VersionMigrator:
    """
    Version migration hook for TrialRecord schema evolution.

    Current behavior:
    - v1 -> v1 : no-op
    """

    def apply(self, record: Dict[str, Any], ctx: FinalizationContext) -> None:
        if ctx.from_version == ctx.to_version:
            return
        raise ValueError(
            f"Unsupported record schema migration: {ctx.from_version} -> {ctx.to_version}"
        )


class RecordFinalizationPipeline:
    def __init__(self, normalizers: list[RecordNormalizer]):
        self.normalizers = list(normalizers)

    def finalize(self, record: Dict[str, Any], ctx: FinalizationContext) -> TrialRecord:
        for normalizer in self.normalizers:
            normalizer.apply(record, ctx)
        return record


DEFAULT_FINALIZATION_PIPELINE = RecordFinalizationPipeline(
    normalizers=[
        VersionMigrator(),
        SchemaDefaultsNormalizer(),
        ProtocolMetadataNormalizer(),
        StrictModeValidator(),
    ]
)

def finalize_record(
    record: Dict[str, Any],
    *,
    phase_name: str | None = None,
    protocol_phase_index: int | None = None,
    protocol_phase_name: str | None = None,
    strict_mode: bool = False,
    from_version: str = "v1",
    to_version: str = "v1",
) -> TrialRecord:
    """
    Normalize record metadata across protocol and phase execution modes.
    """
    ctx = FinalizationContext(
        phase_name=phase_name,
        protocol_phase_index=protocol_phase_index,
        protocol_phase_name=protocol_phase_name,
        strict_mode=strict_mode,
        from_version=from_version,
        to_version=to_version,
    )
    return DEFAULT_FINALIZATION_PIPELINE.finalize(record, ctx)
