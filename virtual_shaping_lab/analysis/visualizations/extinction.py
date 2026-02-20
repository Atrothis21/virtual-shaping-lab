import matplotlib.pyplot as plt

from analysis.visualizations.base import Visualization


class ExtinctionCurvePlot(Visualization):
    """
    Visualization for extinction learning.

    Plots a time-series metric during extinction.
    If multiple metrics are present, the first one is plotted.
    """

    name = "extinction_curve_plot"

    def __init__(self):
        self.fig = None

    def _phase_spans(self, records):
        if not records:
            return []

        phase_key = "subphase" if "subphase" in records[0] else "phase"
        name_key = "subphase_name" if "subphase_name" in records[0] else "phase_name"

        spans = []
        current = records[0].get(phase_key)
        current_name = records[0].get(name_key, str(current))
        start = 0

        for i, r in enumerate(records):
            if r.get(phase_key) != current:
                spans.append((start, i, current_name))
                current = r.get(phase_key)
                current_name = r.get(name_key, str(current))
                start = i

        spans.append((start, len(records), current_name))
        return spans if len(spans) > 1 else []

    def render(self, records, metrics=None) -> None:
        if not records:
            raise ValueError("ExtinctionCurvePlot received no records")

        series = [r.get("prediction") for r in records if r.get("prediction") is not None]

        if not series and metrics:
            metric_name, series = next(iter(metrics.items()))
            if not series:
                raise ValueError(f"ExtinctionCurvePlot received empty series for metric '{metric_name}'")
        elif not series:
            raise ValueError("ExtinctionCurvePlot could not infer series from records")

        self.fig, ax = plt.subplots()
        ax.plot(series)
        ax.set_xlabel("Extinction Trial")
        ax.set_ylabel("Predicted Value")
        ax.set_title("Extinction Curve", pad=18)
        ax.grid(True)
        ax.set_axisbelow(True)

        spans = self._phase_spans(records)
        if spans:
            ymin, ymax = ax.get_ylim()
            ypad = (ymax - ymin) * 0.05
            ax.set_ylim(ymin, ymax + ypad)

            for idx, (start, end, label) in enumerate(spans):
                if idx % 2 == 0:
                    ax.axvspan(start, end - 1, color="#f2f2f2", alpha=0.8, zorder=1)

                if start > 0:
                    ax.axvline(x=start - 0.5, color="#333", linestyle="--", linewidth=1.2, zorder=2)

                mid = (start + end - 1) / 2
                ax.text(
                    mid, 1.02, label,
                    ha="center", va="bottom", fontsize=9,
                    color="#222", transform=ax.get_xaxis_transform()
                )

    def save(self, path) -> None:
        if self.fig is None:
            raise RuntimeError(
                "ExtinctionCurvePlot.render() must be called before save()"
            )

        self.fig.savefig(path)
        plt.close(self.fig)
