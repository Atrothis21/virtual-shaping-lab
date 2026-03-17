import matplotlib
matplotlib.use("Agg")

import pytest
import warnings

from analysis.visualizations.base import Visualization
from analysis.visualizations.time_series import LinePlot
from analysis.visualizations.extinction import ExtinctionCurvePlot
from analysis.visualizations.discrimination import DiscriminationCurvePlot
from analysis.visualizations.dual_time_series import DualTimeSeriesPlot
from analysis.visualizations.auto_time_series import AutoTimeSeriesPlot
from analysis.visualizations.matching_law import MatchingLawPlot
from analysis.visualizations.operant import CumulativeResponsePlot, CumulativeRewardPlot
from analysis.visualizations.operant_diagnostics import (
    RewardTimeSeriesPlot,
    ActionDistributionPlot,
    OutcomeTypeBarPlot,
    PhaseRewardBarPlot,
)
from analysis.visualizations.probe_bar import ProbeBarPlot
from analysis.visualizations.summation import SummationPlot
from analysis.visualizations.stimulus import StimulusBarPlot
from analysis.visualizations.retardation import RetardationCurvePlot
from analysis.visualizations import registry as viz_registry

_TICKLABEL_WARNING_FRAGMENT = "set_ticklabels() should only be used with a fixed number of ticks"


class DummyViz(Visualization):
    name = "dummy"

    def render(self, records, metrics=None, **kwargs) -> None:
        return Visualization.render(self, records, metrics, **kwargs)


def test_visualization_base_render_executes():
    DummyViz().render([], None)


def test_line_plot_errors_and_spans(tmp_path):
    plot = LinePlot()
    with pytest.raises(ValueError):
        plot.render([], {})

    with pytest.raises(ValueError):
        plot.render([{"prediction": None}], {})

    with pytest.raises(ValueError):
        plot.render([{"prediction": None}], {"metric": []})

    records = [
        {"prediction": 0.1, "phase": 0, "phase_name": "A"},
        {"prediction": 0.2, "phase": 1, "phase_name": "B"},
    ]
    plot.render(records, {})
    plot.save(tmp_path / "line.png")


def test_extinction_plot_metrics_fallback(tmp_path):
    plot = ExtinctionCurvePlot()
    with pytest.raises(ValueError):
        plot.render([], {})

    with pytest.raises(ValueError):
        plot.render([{"prediction": None}], {})

    with pytest.raises(ValueError):
        plot.render([{"prediction": None}], {"metric": []})

    records = [
        {"prediction": 0.3, "phase": 0, "phase_name": "ext"},
        {"prediction": 0.1, "phase": 1, "phase_name": "ext2"},
    ]
    plot.render(records, {})
    plot.save(tmp_path / "ext.png")


def test_discrimination_plot_error_and_save(tmp_path):
    plot = DiscriminationCurvePlot()
    with pytest.raises(ValueError):
        plot.render([{"trial": 0, "stimulus_type": "cs_plus", "response": 0.5}], {})

    records = [
        {"trial": 0, "stimulus_type": "cs_plus", "response": 0.8},
        {"trial": 1, "stimulus_type": "cs_minus", "response": 0.2},
    ]
    plot.render(records, {})
    plot.save(tmp_path / "disc.png")

    plot2 = DiscriminationCurvePlot()
    with pytest.raises(RuntimeError):
        plot2.save(tmp_path / "disc2.png")


def test_dual_time_series_branches(tmp_path):
    plot = DualTimeSeriesPlot()
    assert plot._phase_spans([]) == []
    assert plot._resolve_label_map([{"a_stimulus": "tone", "b_stimulus": "noise"}]) == {
        "CS1": "tone",
        "CS2": "noise",
    }

    with pytest.raises(ValueError):
        plot.render([], {})

    with pytest.raises(ValueError):
        plot.render([{"series_values": None}], {})

    records = [
        {
            "series_values": {"CS1": 0.1, "CS2": 0.2},
            "series_labels": {"label_1": "CS1", "label_2": "CS2"},
            "a_stimulus": "tone",
            "b_stimulus": "noise",
            "phase": 0,
            "phase_name": "p1",
        },
        {
            "series_values": {"CS1": 0.2, "CS2": 0.3},
            "series_labels": {"label_1": "CS1", "label_2": "CS2"},
            "a_stimulus": "tone",
            "b_stimulus": "noise",
            "phase": 1,
            "phase_name": "p2",
        },
    ]
    plot.render(records, {})
    plot.save(tmp_path / "dual.png")

    plot2 = DualTimeSeriesPlot()
    with pytest.raises(RuntimeError):
        plot2.save(tmp_path / "dual2.png")


def test_dual_time_series_differential_mode_tracks_cs_plus_and_cs_minus_separately():
    plot = DualTimeSeriesPlot()
    records = [
        {"stimulus_type": "cs_plus", "prediction": 0.7, "trial": 0},
        {"stimulus_type": "cs_minus", "prediction": 0.2, "trial": 1},
        {"stimulus_type": "cs_plus", "prediction": 0.8, "trial": 2},
        {"stimulus_type": "cs_minus", "prediction": 0.3, "trial": 3},
    ]

    plot.render(records, {})
    ax = plot.fig.axes[0]
    lines = {line.get_label(): line for line in ax.lines}

    assert set(lines.keys()) == {"CS+", "CS-"}
    assert list(lines["CS+"].get_xdata()) == [0, 1]
    assert list(lines["CS+"].get_ydata()) == [0.7, 0.8]
    assert list(lines["CS-"].get_xdata()) == [0, 1]
    assert list(lines["CS-"].get_ydata()) == [0.2, 0.3]


def test_discrimination_plot_uses_running_cs_plus_minus_difference():
    plot = DiscriminationCurvePlot()
    records = [
        {"trial": 0, "stimulus_type": "cs_plus", "response": 0.8},
        {"trial": 1, "stimulus_type": "cs_minus", "response": 0.2},
        {"trial": 2, "stimulus_type": "cs_plus", "response": 1.0},
        {"trial": 3, "stimulus_type": "cs_minus", "response": 0.4},
    ]

    plot.render(records, {})
    ax = plot.fig.axes[0]
    line = ax.lines[0]

    assert list(line.get_xdata()) == [1, 2, 3]
    assert list(line.get_ydata()) == pytest.approx([0.6, 0.7, 0.6])


def test_auto_time_series_paths(tmp_path):
    plot = AutoTimeSeriesPlot()
    records_single = [{"series_values": {"A": 0.1}, "prediction": 0.1}]
    plot.render(records_single, {})
    plot.save(tmp_path / "auto1.png")

    plot2 = AutoTimeSeriesPlot()
    records_double = [{"series_values": {"A": 0.1, "B": 0.2}}]
    plot2.render(records_double, {})
    plot2.save(tmp_path / "auto2.png")

    plot3 = AutoTimeSeriesPlot()
    with pytest.raises(RuntimeError):
        plot3.save(tmp_path / "auto3.png")


def test_matching_law_plot(tmp_path):
    plot = MatchingLawPlot()
    records = [
        {"action": 0, "reward": 1.0},
        {"action": 1, "reward": 0.0},
        {"action": 0, "reward": 1.0},
    ]
    plot.render(records, {})
    plot.save(tmp_path / "match.png")

    plot2 = MatchingLawPlot()
    with pytest.raises(RuntimeError):
        plot2.save(tmp_path / "match2.png")


def test_operant_plots(tmp_path):
    resp_plot = CumulativeResponsePlot()
    resp_plot.render([{"action": 0}, {"action": None}, {"action": 1}], {})
    resp_plot.save(tmp_path / "resp.png")

    reward_plot = CumulativeRewardPlot()
    reward_plot.render([{"reward": 1.0}, {"reward": 0.0}], {})
    reward_plot.save(tmp_path / "rew.png")

    resp_plot2 = CumulativeResponsePlot()
    with pytest.raises(KeyError):
        resp_plot2.render([], {})

    reward_plot2 = CumulativeRewardPlot()
    with pytest.raises(KeyError):
        reward_plot2.render([], {})


def test_operant_diagnostic_plots(tmp_path):
    records = [
        {"reward": 1.0, "outcome_type": "reinforcement", "action": 0, "phase_name": "acq"},
        {"reward": 0.0, "outcome_type": "extinction", "action": 0, "phase_name": "acq"},
        {"reward": -1.0, "outcome_type": "punishment", "action": 1, "phase_name": "punish"},
    ]

    reward_ts = RewardTimeSeriesPlot()
    reward_ts.render(records, {})
    reward_ts.save(tmp_path / "reward_ts.png")

    action_dist = ActionDistributionPlot()
    action_dist.render(records, {})
    action_dist.save(tmp_path / "action_dist.png")

    outcome_bar = OutcomeTypeBarPlot()
    outcome_bar.render(records, {})
    outcome_bar.save(tmp_path / "outcome_bar.png")

    phase_bar = PhaseRewardBarPlot()
    phase_bar.render(records, {})
    phase_bar.save(tmp_path / "phase_bar.png")


def test_probe_and_summation_plots(tmp_path):
    probe = ProbeBarPlot()
    with pytest.raises(ValueError):
        probe.render([], {})

    with pytest.raises(ValueError):
        probe.render([{"subphase_name": "probe", "stimulus": None}], {})

    probe.render([{"subphase_name": "probe", "stimulus": "tone", "prediction": 0.5}], {})
    probe.save(tmp_path / "probe.png")

    summation = SummationPlot()
    with pytest.raises(ValueError):
        summation.render([], {})

    with pytest.raises(ValueError):
        summation.render([{"subphase_name": "summation_probe", "stimulus": None}], {})

    summation.render(
        [{"subphase_name": "summation_probe", "stimulus": ("tone", "noise"), "prediction": 0.4}],
        {},
    )
    summation.save(tmp_path / "summation.png")


def test_probe_and_summation_plots_emit_no_ticklabel_warnings():
    probe = ProbeBarPlot()
    summation = SummationPlot()

    with warnings.catch_warnings(record=True) as captured:
        warnings.simplefilter("always")
        probe.render([{"subphase_name": "probe", "stimulus": "tone", "prediction": 0.5}], {})
        summation.render(
            [{"subphase_name": "summation_probe", "stimulus": ("tone", "noise"), "prediction": 0.4}],
            {},
        )

    ticklabel_warnings = [
        w for w in captured if _TICKLABEL_WARNING_FRAGMENT in str(w.message)
    ]
    assert ticklabel_warnings == []


def test_stimulus_bar_plot(tmp_path):
    plot = StimulusBarPlot()
    with pytest.raises(ValueError):
        plot.render([{"stimulus": "tone"}], {})

    plot.render(
        [
            {"stimulus": "tone", "response": 0.3, "stimulus_type": "cs_plus"},
            {"stimulus": "noise", "response": 0.1, "stimulus_type": "cs_minus"},
        ],
        {},
    )
    plot.save(tmp_path / "stim.png")


def test_retardation_plot(tmp_path):
    plot = RetardationCurvePlot()
    with pytest.raises(ValueError):
        plot.render([], {})

    records = [
        {"subphase_name": "retardation", "trial": 0, "response": 0.1, "subphase": 0, "phase_name": "r1"},
        {"subphase_name": "retardation", "trial": 1, "response": 0.2, "subphase": 1, "phase_name": "r2"},
    ]
    plot.render(records, {})
    plot.save(tmp_path / "ret.png")

    plot2 = RetardationCurvePlot()
    with pytest.raises(RuntimeError):
        plot2.save(tmp_path / "ret2.png")


def test_visualization_registry_helpers():
    all_viz = viz_registry.list_visualizations()
    assert "line_plot" in all_viz

    with pytest.raises(ValueError):
        viz_registry.build_visualization("missing_viz")

    viz_registry.render_visualization("line_plot", [{"prediction": 0.1}])
