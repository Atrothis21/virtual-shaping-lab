from collections import defaultdict
import matplotlib.pyplot as plt

from analysis.visualizations.base import Visualization


class StimulusBarPlot(Visualization):
    """
    Bar plot showing mean response grouped by stimulus category
    (e.g. CS+ vs CS-).

    Uses trial-level records.
    """

    name = "stimulus_bar_plot"

    def __init__(self, ylabel: str = "Mean Response"):
        self.ylabel = ylabel
        self.fig = None

    def render(self, records, metrics) -> None:
        """
        Render a bar plot of mean response by stimulus type.

        Parameters
        ----------
        records : list[dict]
            Trial-level records.
        metrics : dict
            Computed metrics (unused, kept for API consistency).
        """
        # ---------------------------------------------
        # Aggregate responses by stimulus label + type
        # ---------------------------------------------
        values = defaultdict(list)

        type_label = {
            "cs_plus": "CS+",
            "cs_minus": "CS−",
        }

        for r in records:
            if "stimulus" not in r or "response" not in r:
                continue

            stim = r["stimulus"]
            stim_type = r.get("stimulus_type")

            if stim_type:
                label = f"{stim} ({type_label.get(stim_type, stim_type)})"
            else:
                label = str(stim)

            values[label].append(r["response"])

        if not values:
            raise ValueError(
                "StimulusBarPlot received no valid records "
                "with 'stimulus' and 'response'."
            )

        labels = list(values.keys())
        means = [sum(v) / len(v) for v in values.values()]

        # ---------------------------------------------
        # Plot
        # ---------------------------------------------
        self.fig, ax = plt.subplots()
        ax.bar(labels, means)
        ax.set_ylabel(self.ylabel)
        ax.set_title("Mean Response by Stimulus")
        ax.grid(axis="y", linestyle="--", alpha=0.6)

        plt.tight_layout()

    def save(self, path) -> None:
        if self.fig is None:
            raise RuntimeError(
                "StimulusBarPlot.render() must be called before save()"
            )

        self.fig.savefig(path)
        plt.close(self.fig)
