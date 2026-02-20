# experiment/phases/series_helpers.py

from typing import Any, Dict, List, Optional


def make_dual_series(
    label_1: str,
    value_1: Optional[float],
    label_2: str,
    value_2: Optional[float],
) -> Dict[str, Dict[str, Optional[float]]]:
    """
    Standardize dual-series payload for trial records.
    """
    return {
        "series_labels": {
            "label_1": label_1,
            "label_2": label_2,
        },
        "series_values": {
            label_1: value_1,
            label_2: value_2,
        },
    }


def phase_stimuli_list(phase: Any) -> List[Any]:
    """
    Extract a flat list of unique stimuli from a phase.
    """
    if hasattr(phase, "stimuli_by_type"):
        values: List[Any] = []
        for items in phase.stimuli_by_type.values():
            if isinstance(items, list):
                values.extend(items)
        return list(dict.fromkeys(values))

    if hasattr(phase, "stimuli") and isinstance(phase.stimuli, list):
        return list(phase.stimuli)

    return []


def attach_reference_stimuli(phases: List[Any]) -> None:
    """
    Ensure single-stimulus phases can reference prior multi-stimulus context.
    """
    last_multi: List[Any] = []

    for phase in phases:
        stimuli = phase_stimuli_list(phase)

        if len(stimuli) >= 2:
            last_multi = stimuli
            continue

        if len(stimuli) == 1 and last_multi:
            target = stimuli[0]
            reference = [s for s in last_multi if s != target]
            if reference and not phase.params.get("reference_stimuli"):
                phase.params["reference_stimuli"] = reference
                if hasattr(phase, "reference_stimuli"):
                    phase.reference_stimuli = list(reference)
                if hasattr(phase, "target_stimulus"):
                    phase.target_stimulus = target
