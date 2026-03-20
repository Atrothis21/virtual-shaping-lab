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
    "step": None,
    "tick": None,
    "t_s": None,
    "dt_s": None,
    "trial_step": None,
    "trial_id": None,
    "episode_id": None,
    "rollout_id": None,
    "context": None,
    "stimulus": None,
    "stimulus_type": None,
    "action": None,
    "policy_state": None,
    "response": None,
    "reward": None,
    "prediction": None,
    "prediction_error": None,
    "outcome_type": None,
    "schedule": None,
    "done": None,
    "terminal": None,
    "terminal_reason": None,
    "horizon_stop_reason": None,
    "learning_enabled": None,
    "metadata": {},
}

_DEBUG_TELEMETRY_FIELD_TYPES: dict[str, tuple[type, ...]] = {
    "value": (int, float),
    "prediction_error": (int, float),
    "active_features": (list, tuple),
    "attention_effective": (dict,),
    "alpha_by_stimulus": (dict,),
    "mean_alpha": (int, float),
    "cuewise_contributions": (dict,),
    "salience_effective": (dict,),
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
        if record.get("step") is None:
            if record.get("trial_step") is not None:
                record["step"] = record.get("trial_step")
            else:
                record["step"] = record.get("tick")
        if record.get("prediction_error") is None:
            debug = record.get("debug")
            if isinstance(debug, dict):
                record["prediction_error"] = debug.get("prediction_error")
        if record.get("policy_state") is None:
            metadata = record.get("metadata")
            if isinstance(metadata, dict):
                candidate = metadata.get("policy_state")
                if isinstance(candidate, dict):
                    record["policy_state"] = dict(candidate)
        if record.get("terminal") is None:
            done = record.get("done")
            if isinstance(done, bool):
                record["terminal"] = done
        if record.get("terminal_reason") is None:
            metadata = record.get("metadata")
            if isinstance(metadata, dict):
                termination = metadata.get("termination")
                if isinstance(termination, dict):
                    reason = termination.get("reason")
                    if isinstance(reason, str) and reason.strip():
                        record["terminal_reason"] = reason
        if record.get("horizon_stop_reason") is None:
            terminal_reason = record.get("terminal_reason")
            if isinstance(terminal_reason, str) and "horizon" in terminal_reason.lower():
                record["horizon_stop_reason"] = terminal_reason


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


class DebugTelemetrySchemaValidator:
    """
    Validate opt-in runtime debug telemetry block shape when present.
    """

    def apply(self, record: Dict[str, Any], ctx: FinalizationContext) -> None:
        debug = record.get("debug")
        if debug is None:
            return
        if not isinstance(debug, dict):
            raise ValueError("Record debug telemetry must be an object when provided.")
        for key, value in debug.items():
            if key not in _DEBUG_TELEMETRY_FIELD_TYPES:
                raise ValueError(f"Unknown debug telemetry field: {key}")
            if value is None:
                continue
            allowed = _DEBUG_TELEMETRY_FIELD_TYPES[key]
            if not isinstance(value, allowed):
                names = ", ".join(t.__name__ for t in allowed)
                raise ValueError(f"Debug telemetry field '{key}' must be of type: {names}")
            if key == "active_features":
                for feature in value:
                    if not isinstance(feature, str):
                        raise ValueError("Debug telemetry field 'active_features' must contain strings.")


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
        DebugTelemetrySchemaValidator(),
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
