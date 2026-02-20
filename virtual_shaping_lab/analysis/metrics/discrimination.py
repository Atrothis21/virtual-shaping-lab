# analysis/metrics/discrimination.py

from typing import Dict, List, Any


class DiscriminationIndex:
    """
    Discrimination index between two stimulus categories
    (e.g. CS+ vs CS-).

    Computes the difference in mean response value between
    records labeled with positive_key and negative_key
    in the 'stimulus_type' field.
    """

    name = "discrimination_index"

    def __init__(self, positive_key: str, negative_key: str):
        self.positive_key = positive_key
        self.negative_key = negative_key

    def compute(self, records: List[Dict[str, Any]]) -> float:
        pos_values = []
        neg_values = []

        for r in records:
            # -----------------------------------------
            # Validation
            # -----------------------------------------
            if "stimulus_type" not in r or "response" not in r:
                raise KeyError(
                    "Record missing required keys 'stimulus_type' or 'response'. "
                    f"Available keys: {list(r.keys())}"
                )

            stim_type = r["stimulus_type"]
            response = r["response"]

            # -----------------------------------------
            # Accumulate responses by stimulus category
            # -----------------------------------------
            if stim_type == self.positive_key:
                pos_values.append(response)
            elif stim_type == self.negative_key:
                neg_values.append(response)

        # ---------------------------------------------
        # Sanity check
        # ---------------------------------------------
        if not pos_values or not neg_values:
            raise ValueError(
                f"Insufficient data to compute discrimination index: "
                f"{self.positive_key} ({len(pos_values)}), "
                f"{self.negative_key} ({len(neg_values)})"
            )

        # ---------------------------------------------
        # Discrimination index
        # ---------------------------------------------
        mean_pos = sum(pos_values) / len(pos_values)
        mean_neg = sum(neg_values) / len(neg_values)

        return mean_pos - mean_neg
