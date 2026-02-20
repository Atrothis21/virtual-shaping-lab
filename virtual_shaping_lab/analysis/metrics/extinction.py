# analysis/metrics/extinction.py

from typing import Any, Dict, List
from analysis.metrics.base import Metric


class ExtinctionRate(Metric):
    """
    Estimate extinction rate as the slope of prediction decay.

    Computed as a simple linear regression slope of
    prediction vs trial index.

    More negative values indicate faster extinction.
    """

    name = "extinction_rate"

    def compute(self, records: List[Dict[str, Any]]) -> float:
        predictions = [r["prediction"] for r in records]
        n = len(predictions)

        if n < 2:
            raise ValueError("ExtinctionRate requires at least 2 trials")

        # Simple linear regression slope
        x = list(range(n))
        x_mean = sum(x) / n
        y_mean = sum(predictions) / n

        numerator = sum(
            (x[i] - x_mean) * (predictions[i] - y_mean)
            for i in range(n)
        )
        denominator = sum(
            (x[i] - x_mean) ** 2
            for i in range(n)
        )

        if denominator == 0:
            return 0.0

        return numerator / denominator


class TrialsToCriterion(Metric):
    """
    Compute number of trials until prediction falls below a criterion.

    Common extinction measure in behavioral experiments.
    """

    name = "trials_to_criterion"

    def __init__(self, criterion: float = 0.1):
        """
        Parameters
        ----------
        criterion : float
            Threshold below which responding is considered extinguished
        """
        self.criterion = criterion

    def compute(self, records: List[Dict[str, Any]]) -> int:
        for i, r in enumerate(records):
            if r["prediction"] <= self.criterion:
                return i
        return len(records)


class AreaUnderExtinctionCurve(Metric):
    """
    Compute area under the extinction curve (AUC).

    Larger values indicate greater resistance to extinction.
    """

    name = "extinction_auc"

    def compute(self, records: List[Dict[str, Any]]) -> float:
        predictions = [r["prediction"] for r in records]
        return sum(predictions)


class ExtinctionOverTime(Metric):
    """
    Return prediction values over extinction trials.

    This is a semantic alias for a learning curve during extinction,
    provided for conceptual clarity in reports.
    """

    name = "extinction_over_time"

    def compute(self, records: List[Dict[str, Any]]) -> List[float]:
        return [r["prediction"] for r in records]
