# analysis/metrics/stimulus_statistics.py

from collections import defaultdict
from typing import Dict, List, Any

from analysis.metrics.base import StimulusMetric


# -------------------------------------------------
# Helpers
# -------------------------------------------------

def _stimulus_key(record: Dict[str, Any]) -> str:
    if "stimulus" not in record:
        raise KeyError(
            "Record missing required key 'stimulus'. "
            f"Available keys: {list(record.keys())}"
        )
    return record["stimulus"]


def _prediction_value(record: Dict[str, Any]) -> float:
    if "response" not in record:
        raise KeyError(
            "Record missing required key 'response'. "
            f"Available keys: {list(record.keys())}"
        )
    return record["response"]


# -------------------------------------------------
# Base class for stimulus statistics
# -------------------------------------------------

class _StimulusStatistic(StimulusMetric):

    def _group_by_stimulus(self, records: List[Dict[str, Any]]):
        grouped = defaultdict(list)
        for r in records:
            grouped[_stimulus_key(r)].append(r)
        return grouped


# -------------------------------------------------
# Concrete metrics
# -------------------------------------------------

class MeanPredictionByStimulus(_StimulusStatistic):
    name = "mean_prediction_by_stimulus"

    def _compute_by_stimulus(self, records: List[Dict[str, Any]]) -> Dict[str, float]:
        grouped = self._group_by_stimulus(records)
        return {
            stim: sum(_prediction_value(r) for r in rs) / len(rs)
            for stim, rs in grouped.items()
        }


class FinalPredictionByStimulus(_StimulusStatistic):
    name = "final_prediction_by_stimulus"

    def _compute_by_stimulus(self, records: List[Dict[str, Any]]) -> Dict[str, float]:
        grouped = self._group_by_stimulus(records)
        return {
            stim: _prediction_value(rs[-1])
            for stim, rs in grouped.items()
        }


class MeanRewardByStimulus(_StimulusStatistic):
    name = "mean_reward_by_stimulus"

    def _compute_by_stimulus(self, records: List[Dict[str, Any]]) -> Dict[str, float]:
        grouped = self._group_by_stimulus(records)
        return {
            stim: sum(r["reward"] for r in rs) / len(rs)
            for stim, rs in grouped.items()
        }


class TrialCountByStimulus(_StimulusStatistic):
    name = "trial_count_by_stimulus"

    def _compute_by_stimulus(self, records: List[Dict[str, Any]]) -> Dict[str, int]:
        grouped = self._group_by_stimulus(records)
        return {stim: len(rs) for stim, rs in grouped.items()}
