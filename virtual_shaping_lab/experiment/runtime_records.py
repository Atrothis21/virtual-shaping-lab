# experiment/runtime_records.py

from typing import Any, Dict


def finalize_record(
    record: Dict[str, Any],
    *,
    phase_name: str | None = None,
    protocol_phase_index: int | None = None,
    protocol_phase_name: str | None = None,
) -> Dict[str, Any]:
    """
    Normalize record metadata across protocol and phase execution modes.
    """
    if phase_name and "phase_name" not in record:
        record["phase_name"] = phase_name
    if protocol_phase_index is not None:
        record.setdefault("subphase", protocol_phase_index)
    if protocol_phase_name:
        record.setdefault("subphase_name", protocol_phase_name)
    return record
