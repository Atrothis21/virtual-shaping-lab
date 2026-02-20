# analysis/metrics/operant.py

from typing import Any, Dict, List
from analysis.metrics.base import TimeSeriesMetric


class CumulativeResponses(TimeSeriesMetric):
    """
    Cumulative number of responses over trials.

    Each operant trial produces exactly one response.
    """

    name = "cumulative_responses"

    def _compute_series(
        self,
        records: List[Dict[str, Any]]
    ) -> List[int]:
        cumulative = []
        total = 0

        for _ in records:
            total += 1
            cumulative.append(total)

        return cumulative


class CumulativeRewards(TimeSeriesMetric):
    """
    Cumulative sum of rewards over trials.
    """

    name = "cumulative_rewards"

    def _compute_series(
        self,
        records: List[Dict[str, Any]]
    ) -> List[float]:
        cumulative = []
        total = 0.0

        for record in records:
            total += record.get("reward", 0.0)
            cumulative.append(total)

        return cumulative
