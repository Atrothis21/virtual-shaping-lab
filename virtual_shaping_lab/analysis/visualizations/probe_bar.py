from collections import defaultdict
import matplotlib.pyplot as plt

from analysis.visualizations.base import Visualization


class ProbeBarPlot(Visualization):
    """
    Bar plot of mean prediction by stimulus during probe phase.
    """

    name = "probe_bar_plot"

    def __init__(self):
        self.fig = None

    def render(self, records, metrics) -> None:
        probe_records = [
            r for r in records
            if r.get("subphase_name") == "probe"
        ]

        if not probe_records:
            raise ValueError("ProbeBarPlot received no probe records")

        values = defaultdict(list)

        for r in probe_records:
            stim = r.get("stimulus")
            if stim is None:
                continue

            # Prefer prediction for probe interpretation
            value = r.get("prediction")
            if value is None:
                value = r.get("response")

            if value is None:
                continue

            values[stim].append(value)

        if not values:
            raise ValueError("ProbeBarPlot received no valid probe records")

        def fmt(stim):
            if isinstance(stim, tuple):
                return "+".join(str(x) for x in stim)
            return str(stim)

        labels = [fmt(k) for k in values.keys()]
        means = [sum(v) / len(v) for v in values.values()]
        x_positions = list(range(len(labels)))

        self.fig, ax = plt.subplots()
        ax.bar(x_positions, means)
        ax.set_ylabel("Prediction")
        ax.set_title("Final Probe Predictions", pad=18)
        ax.grid(axis="y", linestyle="--", alpha=0.6)
        ax.set_xticks(x_positions)
        ax.set_xticklabels(labels, rotation=20, ha="right")

    def save(self, path) -> None:
        if self.fig is None:
            raise RuntimeError("ProbeBarPlot.render() must be called before save()")

        self.fig.savefig(path)
        plt.close(self.fig)
