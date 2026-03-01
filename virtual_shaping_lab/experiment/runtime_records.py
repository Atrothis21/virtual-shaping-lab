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


class RecordFinalizationPipeline:
    def __init__(self, normalizers: list[RecordNormalizer]):
        self.normalizers = list(normalizers)

    def finalize(self, record: Dict[str, Any], ctx: FinalizationContext) -> TrialRecord:
        for normalizer in self.normalizers:
            normalizer.apply(record, ctx)
        return record


DEFAULT_FINALIZATION_PIPELINE = RecordFinalizationPipeline(
    normalizers=[
        SchemaDefaultsNormalizer(),
        ProtocolMetadataNormalizer(),
    ]
)

def finalize_record(
    record: Dict[str, Any],
    *,
    phase_name: str | None = None,
    protocol_phase_index: int | None = None,
    protocol_phase_name: str | None = None,
) -> TrialRecord:
    """
    Normalize record metadata across protocol and phase execution modes.
    """
    ctx = FinalizationContext(
        phase_name=phase_name,
        protocol_phase_index=protocol_phase_index,
        protocol_phase_name=protocol_phase_name,
    )
    return DEFAULT_FINALIZATION_PIPELINE.finalize(record, ctx)
