# analysis/visualizations/auto_time_series.py

from analysis.visualizations.base import Visualization
from analysis.visualizations.time_series import LinePlot
from analysis.visualizations.dual_time_series import DualTimeSeriesPlot


class AutoTimeSeriesPlot(Visualization):
    """
    Auto-select between line_plot and dual_time_series_plot.

    - If records contain two series in series_values -> dual_time_series_plot
    - Otherwise -> line_plot
    """

    name = "auto_time_series_plot"

    def __init__(self):
        self._plot = None

    def _has_two_series(self, records) -> bool:
        labels = set()

        for r in records:
            sv = r.get("series_values")
            if not isinstance(sv, dict):
                continue

            for name, val in sv.items():
                if val is not None:
                    labels.add(name)

            if len(labels) >= 2:
                return True

        return False

    def render(self, records, metrics=None) -> None:
        if self._has_two_series(records):
            self._plot = DualTimeSeriesPlot()
            self._plot.render(records, metrics or {})
        else:
            self._plot = LinePlot()
            self._plot.render(records, metrics)

    def save(self, path) -> None:
        if self._plot is None:
            raise RuntimeError("AutoTimeSeriesPlot.render() must be called before save()")
        self._plot.save(path)
