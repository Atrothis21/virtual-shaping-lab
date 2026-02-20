from typing import Dict, Any, List
import matplotlib.pyplot as plt

from analysis.visualizations.base import Visualization


class DiscriminationCurvePlot(Visualization):
    """
    Plot discrimination index over trials:
    mean(CS+) - mean(CS-) as a function of trial number.
    """

    name = "discrimination_curve_plot"

    def __init__(self):
        self.fig = None

    def render(
        self,
        records: List[Dict[str, Any]],
        metrics: Dict[str, Any],
    ) -> None:
        """
        Render discrimination curve over trials.

        Parameters
        ----------
        records : list[dict]
            Trial-level records.
        metrics : dict
            Computed metrics (unused here).
        """
        # ---------------------------------------------
        # Sort records by trial
        # ---------------------------------------------
        records = sorted(records, key=lambda r: r["trial"])

        cs_plus_responses = []
        cs_minus_responses = []

        di_values = []
        trials = []

        for r in records:
            stim_type = r.get("stimulus_type")
            response = r.get("response")

            if stim_type == "cs_plus":
                cs_plus_responses.append(response)
            elif stim_type == "cs_minus":
                cs_minus_responses.append(response)

            # Only compute DI once we have both
            if cs_plus_responses and cs_minus_responses:
                mean_pos = sum(cs_plus_responses) / len(cs_plus_responses)
                mean_neg = sum(cs_minus_responses) / len(cs_minus_responses)
                di = mean_pos - mean_neg

                trials.append(r["trial"])
                di_values.append(di)

        if not di_values:
            raise ValueError(
                "Insufficient data to render discrimination curve plot."
            )

        # ---------------------------------------------
        # Plot
        # ---------------------------------------------
        self.fig, ax = plt.subplots()
        ax.plot(trials, di_values, label="Discrimination Index")
        ax.axhline(0, linestyle="--", linewidth=1)
        ax.set_xlabel("Trial")
        ax.set_ylabel("Discrimination Index")
        ax.set_title("Discrimination Index Over Trials")
        ax.legend()
        ax.grid(alpha=0.5)

        plt.tight_layout()

    def save(self, path) -> None:
        if self.fig is None:
            raise RuntimeError(
                "DiscriminationCurvePlot.render() must be called before save()"
            )

        self.fig.savefig(path)
        plt.close(self.fig)
