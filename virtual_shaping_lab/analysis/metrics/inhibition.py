# analysis/metrics/inhibition.py

from typing import Dict, List, Any


class InhibitoryStrength:
    """
    Inhibitory strength metric.

    Measures how strongly an inhibitory stimulus suppresses
    responding relative to a baseline stimulus.
    """

    name = "inhibitory_strength"

    def __init__(self, inhibitory_key: str = "CS-", baseline_key: str = "CS+"):
        self.inhibitory_key = inhibitory_key
        self.baseline_key = baseline_key

    def compute(self, records: List[Dict[str, Any]]) -> float:
        inhibitory_values = []
        baseline_values = []

        for r in records:
            if "stimulus" not in r:
                raise KeyError(
                    "Record missing required key 'stimulus'. "
                    f"Available keys: {list(r.keys())}"
                )

            stim = r["stimulus"]

            if stim == self.inhibitory_key:
                inhibitory_values.append(r["prediction"])
            elif stim == self.baseline_key:
                baseline_values.append(r["prediction"])

        if not inhibitory_values or not baseline_values:
            raise ValueError(
                f"Insufficient data to compute inhibitory strength: "
                f"{self.inhibitory_key} ({len(inhibitory_values)}), "
                f"{self.baseline_key} ({len(baseline_values)})"
            )

        return (sum(baseline_values) / len(baseline_values)) - (
            sum(inhibitory_values) / len(inhibitory_values)
        )
