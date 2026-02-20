# analysis/metrics/time_series.py

from typing import Any, Dict, List
from analysis.metrics.base import TimeSeriesMetric


class PredictionTimeSeries(TimeSeriesMetric):
    """
    Prediction (value estimate) over trials.

    This is the canonical learning curve for:
    - classical conditioning
    - extinction
    - operant conditioning
    """

    name = "prediction_time_series"

    def _compute_series(
        self,
        records: List[Dict[str, Any]]
    ) -> List[float]:
        return [r["prediction"] for r in records]


class RewardTimeSeries(TimeSeriesMetric):
    """
    Reward received over trials.

    Useful for:
    - verifying reinforcement schedules
    - partial reinforcement
    - operant schedules
    """

    name = "reward_time_series"

    def _compute_series(
        self,
        records: List[Dict[str, Any]]
    ) -> List[float]:
        return [r["reward"] for r in records]


class PredictionErrorTimeSeries(TimeSeriesMetric):
    """
    Prediction error over trials.

    Computed as:
        reward - prediction

    This is learner-agnostic and works for:
    - Rescorla–Wagner
    - TD-style learners
    """

    name = "prediction_error_time_series"

    def _compute_series(
        self,
        records: List[Dict[str, Any]]
    ) -> List[float]:
        return [
            r["reward"] - r["prediction"]
            for r in records
        ]


class ActionTimeSeries(TimeSeriesMetric):
    """
    Action selection over trials (if applicable).

    For classical conditioning, this will be a list of None.
    For operant conditioning, this captures behavior.
    """

    name = "action_time_series"

    def _compute_series(
        self,
        records: List[Dict[str, Any]]
    ) -> List[Any]:
        return [r.get("action") for r in records]
