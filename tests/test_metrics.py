import pytest

from analysis.metrics.base import Metric, TimeSeriesMetric, StimulusMetric
from analysis.metrics.discrimination import DiscriminationIndex
from analysis.metrics.extinction import (
    ExtinctionRate,
    TrialsToCriterion,
    AreaUnderExtinctionCurve,
    ExtinctionOverTime,
)
from analysis.metrics.inhibition import InhibitoryStrength
from analysis.metrics.stimulus_statistics import _stimulus_key, _prediction_value
from analysis.metrics.time_series import (
    PredictionTimeSeries,
    RewardTimeSeries,
    PredictionErrorTimeSeries,
    ActionTimeSeries,
)
from analysis.metrics import registry as metric_registry
from analysis.metrics.operant import (
    OutcomeTypeCounts,
    ActionCounts,
    PhaseRewardSummary,
)


class DummyMetric(Metric):
    name = "dummy_metric"

    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def compute(self, records):
        return {"count": len(records)}


class DummySeries(TimeSeriesMetric):
    name = "dummy_series"

    def _compute_series(self, records):
        return [r.get("prediction") for r in records]


class DummyStimulus(StimulusMetric):
    name = "dummy_stimulus"

    def _compute_by_stimulus(self, records):
        return {"x": 1}


def test_metric_base_abstract_paths():
    assert DummyMetric().compute([]) == {"count": 0}
    assert DummySeries().compute([{"prediction": 1.0}]) == [1.0]
    assert DummyStimulus().compute([{"stimulus": "tone"}]) == {"x": 1}


def test_discrimination_index_errors():
    metric = DiscriminationIndex("cs_plus", "cs_minus")
    with pytest.raises(KeyError):
        metric.compute([{"response": 0.1}])
    with pytest.raises(ValueError):
        metric.compute([{"stimulus_type": "cs_plus", "response": 0.5}])


def test_extinction_metrics():
    rate = ExtinctionRate()
    with pytest.raises(ValueError):
        rate.compute([{"prediction": 0.1}])

    assert rate.compute([{"prediction": 1.0}, {"prediction": 1.0}]) == 0.0

    trials = TrialsToCriterion(criterion=0.2)
    assert trials.compute([{"prediction": 0.5}, {"prediction": 0.1}]) == 1
    assert trials.compute([{"prediction": 0.5}, {"prediction": 0.4}]) == 2

    auc = AreaUnderExtinctionCurve()
    assert auc.compute([{"prediction": 0.1}, {"prediction": 0.2}]) == pytest.approx(0.3)

    ext = ExtinctionOverTime()
    assert ext.compute([{"prediction": 0.3}]) == [0.3]


def test_inhibitory_strength_errors():
    metric = InhibitoryStrength(inhibitory_key="CS-", baseline_key="CS+")
    with pytest.raises(KeyError):
        metric.compute([{"prediction": 0.1}])
    with pytest.raises(ValueError):
        metric.compute([{"stimulus": "CS+", "prediction": 0.2}])


def test_stimulus_statistics_helpers_errors():
    with pytest.raises(KeyError):
        _stimulus_key({"response": 0.1})
    with pytest.raises(KeyError):
        _prediction_value({"stimulus": "tone"})


def test_time_series_metrics():
    records = [
        {"prediction": 0.1, "reward": 1.0, "action": 0},
        {"prediction": 0.2, "reward": 0.0, "action": None},
    ]
    assert PredictionTimeSeries().compute(records) == [0.1, 0.2]
    assert RewardTimeSeries().compute(records) == [1.0, 0.0]
    assert PredictionErrorTimeSeries().compute(records) == [0.9, -0.2]
    assert ActionTimeSeries().compute(records) == [0, None]


def test_metrics_registry_helpers(monkeypatch):
    monkeypatch.setattr(metric_registry, "METRIC_REGISTRY", {DummyMetric.name: DummyMetric})
    names = metric_registry.list_metrics()
    assert names == [DummyMetric.name]

    with pytest.raises(KeyError):
        metric_registry.validate_metric("missing_metric")

    metric = metric_registry.build_metric(DummyMetric.name, foo="bar")
    assert isinstance(metric, DummyMetric)
    assert metric.kwargs["foo"] == "bar"
    result = metric_registry.compute_metric(DummyMetric.name, records=[{"a": 1}, {"a": 2}])
    assert result == {"count": 2}


def test_operant_diagnostic_metrics():
    records = [
        {"reward": 1.0, "outcome_type": "reinforcement", "action": 0, "subphase_name": "acq"},
        {"reward": 0.0, "outcome_type": "extinction", "action": 0, "subphase_name": "acq"},
        {"reward": -1.0, "outcome_type": "punishment", "action": 1, "subphase_name": "punish"},
    ]

    assert OutcomeTypeCounts().compute(records) == {
        "reinforcement": 1,
        "extinction": 1,
        "punishment": 1,
    }

    action_counts = ActionCounts().compute(records)
    assert action_counts["0"] == 2
    assert action_counts["1"] == 1

    summary = PhaseRewardSummary().compute(records)
    assert "acq" in summary
    assert summary["acq"]["mean_reward"] == pytest.approx(0.5, abs=1e-12)
