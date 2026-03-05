# analysis/visualizations/summation.py

from collections import defaultdict
import matplotlib.pyplot as plt

from analysis.visualizations.base import Visualization


class SummationPlot(Visualization):
    """
    Visualization for conditioned inhibition summation tests.

    Reads only the 'summation_probe' phase and plots B vs BX.
    """

    name = "summation_plot"

    def __init__(self):
        self.fig = None

    def render(self, records, metrics) -> None:
        summation_records = [
            r for r in records
            if r.get("subphase_name") == "summation_probe"
        ]

        if not summation_records:
            raise ValueError("SummationPlot received no summation probe records")

        values = defaultdict(list)

        for r in summation_records:
            stim = r.get("stimulus")
            if stim is None:
                continue

            value = r.get("prediction")
            if value is None:
                value = r.get("response")

            if value is None:
                continue

            values[stim].append(value)

        if not values:
            raise ValueError("SummationPlot received no valid summation records")

        def fmt(stim):
            if isinstance(stim, tuple) or isinstance(stim, list):
                return "+".join(str(x) for x in stim)
            return str(stim)

        labels = [fmt(k) for k in values.keys()]
        means = [sum(v) / len(v) for v in values.values()]
        x_positions = list(range(len(labels)))

        self.fig, ax = plt.subplots()
        ax.bar(x_positions, means)
        ax.set_ylabel("Prediction")
        ax.set_title("Conditioned Inhibition: Summation Test", pad=18)
        ax.grid(axis="y", linestyle="--", alpha=0.6)
        ax.set_xticks(x_positions)
        ax.set_xticklabels(labels, rotation=20, ha="right")

    def save(self, path) -> None:
        if self.fig is None:
            raise RuntimeError("SummationPlot.render() must be called before save()")

        self.fig.savefig(path)
        plt.close(self.fig)
