# experiment/runner.py

from typing import List, Dict, Any, Protocol, runtime_checkable

from experiment.phases.series_helpers import attach_reference_stimuli
from experiment.runtime_records import finalize_record


@runtime_checkable
class ProtocolLike(Protocol):
    def run(self) -> List[Dict[str, Any]]: ...


@runtime_checkable
class PhaseLike(Protocol):
    def has_next_trial(self) -> bool: ...
    def step(self) -> Dict[str, Any] | None: ...


class Runner:
    """
    Execute runtime units and collect trial records.

    The runner is intentionally thin:
    - It does NOT control trial logic
    - It does NOT inspect internals beyond run/step
    - It simply delegates execution
    """

    def __init__(self, runtime_units):
        self.runtime_units = runtime_units

    def _run_phase(self, phase: PhaseLike) -> List[Dict[str, Any]]:
        records: List[Dict[str, Any]] = []
        while phase.has_next_trial():
            record = phase.step()
            if record is not None:
                finalize_record(
                    record,
                    phase_name=record.get("phase"),
                )
                records.append(record)
        return records

    def run(self) -> List[Dict[str, Any]]:
        """
        Run protocols/phases to completion.

        Returns
        -------
        records : list of dict
            One record per trial, suitable for analysis.
        """
        units = self.runtime_units
        if not isinstance(units, list):
            units = [units]

        records: List[Dict[str, Any]] = []

        # Attach reference stimuli across phase-mode sequences
        if units and isinstance(units[0], PhaseLike):
            attach_reference_stimuli(units)

        for unit in units:
            if isinstance(unit, ProtocolLike):
                records.extend(unit.run())
            elif isinstance(unit, PhaseLike):
                records.extend(self._run_phase(unit))
            else:
                raise TypeError(
                    f"Unsupported runtime unit: {type(unit).__name__} "
                    "must implement run() or (has_next_trial + step)."
                )

        return records
