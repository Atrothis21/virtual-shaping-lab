# analysis/metrics/base.py

from abc import ABC, abstractmethod
from typing import Any, Dict, Iterable, List


class Metric(ABC):
    """
    Base class for all analysis metrics.

    A Metric:
    - Consumes experiment records
    - Produces derived data (numbers, lists, dicts)
    - Does NOT modify records
    - Does NOT know about protocols, agents, or learners

    Metrics should be:
    - Deterministic
    - Stateless
    - JSON-serializable in output
    """

    name: str = "metric"

    @abstractmethod
    def compute(self, records: List[Dict[str, Any]]) -> Any:
        """
        Compute the metric from experiment records.

        Parameters
        ----------
        records : list of dict
            Output of experiment.runner.run_experiment

        Returns
        -------
        Any
            Metric-specific output (float, list, dict, etc.)
        """
        pass


class TimeSeriesMetric(Metric):
    """
    Base class for metrics that return values per trial.

    Example outputs:
    - learning curves
    - reward over time
    - prediction error over time
    """

    def compute(self, records: List[Dict[str, Any]]) -> List[Any]:
        return self._compute_series(records)

    @abstractmethod
    def _compute_series(
        self,
        records: List[Dict[str, Any]]
    ) -> List[Any]:
        pass


class StimulusMetric(Metric):
    """
    Base class for metrics that aggregate over stimuli.

    Stimuli are identified using the `state` field of records,
    which may be:
    - a single feature
    - a compound list of features
    """

    def compute(self, records: List[Dict[str, Any]]) -> Dict[Any, Any]:
        return self._compute_by_stimulus(records)

    @abstractmethod
    def _compute_by_stimulus(
        self,
        records: List[Dict[str, Any]]
    ) -> Dict[Any, Any]:
        pass
