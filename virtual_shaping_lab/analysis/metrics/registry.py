# analysis/metrics/registry.py

"""
Metric registry.

This module is the single source of truth for all available
analysis metrics. Metrics are ATOMIC; higher-level groupings
(e.g. "stimulus_statistics") belong in report presets, not here.
"""

# -------------------------------------------------
# Base class
# -------------------------------------------------

from analysis.metrics.base import Metric

# -------------------------------------------------
# Time-series metrics
# -------------------------------------------------

from analysis.metrics.time_series import (
    PredictionTimeSeries,
    RewardTimeSeries,
)

# -------------------------------------------------
# Stimulus-level statistics
# -------------------------------------------------

from analysis.metrics.stimulus_statistics import (
    MeanPredictionByStimulus,
    FinalPredictionByStimulus,
    MeanRewardByStimulus,
    TrialCountByStimulus,
)

# -------------------------------------------------
# Higher-level analyses
# -------------------------------------------------

from analysis.metrics.discrimination import DiscriminationIndex
from analysis.metrics.inhibition import InhibitoryStrength
from analysis.metrics.extinction import ExtinctionRate

# -------------------------------------------------
# Operant conditioning metrics
# -------------------------------------------------

from analysis.metrics.operant import (
    CumulativeResponses,
    CumulativeRewards,
)

# -------------------------------------------------
# Registry: string -> metric class
# -------------------------------------------------

METRIC_REGISTRY = {
    # ---- time series ----
    PredictionTimeSeries.name: PredictionTimeSeries,
    RewardTimeSeries.name: RewardTimeSeries,

    # ---- stimulus statistics ----
    MeanPredictionByStimulus.name: MeanPredictionByStimulus,
    FinalPredictionByStimulus.name: FinalPredictionByStimulus,
    MeanRewardByStimulus.name: MeanRewardByStimulus,
    TrialCountByStimulus.name: TrialCountByStimulus,

    # ---- higher-level indices ----
    DiscriminationIndex.name: DiscriminationIndex,
    InhibitoryStrength.name: InhibitoryStrength,
    ExtinctionRate.name: ExtinctionRate,

    # ---- operant conditioning ----
    CumulativeResponses.name: CumulativeResponses,
    CumulativeRewards.name: CumulativeRewards,
}



# -------------------------------------------------
# Public helpers
# -------------------------------------------------

def list_metrics():
    """
    Return a sorted list of available metric names.
    """
    return sorted(METRIC_REGISTRY.keys())


def validate_metric(name: str):
    """
    Validate that a metric exists in the registry.
    """
    if name not in METRIC_REGISTRY:
        available = ", ".join(list_metrics())
        raise KeyError(
            f"Unknown metric '{name}'. "
            f"Available metrics: {available}"
        )


def build_metric(name: str, **params) -> Metric:
    """
    Instantiate a metric by name.
    """
    validate_metric(name)
    return METRIC_REGISTRY[name](**params)


def compute_metric(name: str, records, **params):
    """
    Convenience wrapper: build and compute a metric in one call.
    """
    metric = build_metric(name, **params)
    return metric.compute(records)
