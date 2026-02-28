# experiment/runtime_records.py

from typing import Any, Dict

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


def _apply_record_schema_defaults(record: Dict[str, Any]) -> None:
    for key, default in _TRIAL_RECORD_DEFAULTS.items():
        if key not in record:
            record[key] = {} if key == "metadata" else default

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
    _apply_record_schema_defaults(record)

    if phase_name:
        if record.get("phase_name") is None:
            record["phase_name"] = phase_name
        if record.get("phase") is None:
            record["phase"] = phase_name
    if protocol_phase_index is not None:
        if record.get("subphase") is None:
            record["subphase"] = protocol_phase_index
    if protocol_phase_name:
        if record.get("subphase_name") is None:
            record["subphase_name"] = protocol_phase_name
    return record
