from typing import Dict, Any, List
import matplotlib.pyplot as plt

from analysis.visualizations.base import Visualization


class RetardationCurvePlot(Visualization):
    """
    Plot acquisition curve during retardation phase (X -> US).
    """

    name = "retardation_curve_plot"

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

    def render(
        self,
        records: List[Dict[str, Any]],
        metrics: Dict[str, Any],
    ) -> None:
        # Filter to retardation phase only
        retardation_records = [
            r for r in records
            if r.get("subphase_name") == "retardation"
        ]

        if not retardation_records:
            raise ValueError("RetardationCurvePlot received no retardation records")

        retardation_records = sorted(retardation_records, key=lambda r: r["trial"])

        trials, values = [], []
        responses = []

        for r in retardation_records:
            responses.append(r["response"])
            trials.append(r["trial"])
            values.append(sum(responses) / len(responses))

        self.fig, ax = plt.subplots()
        ax.plot(trials, values)
        ax.set_xlabel("Trial")
        ax.set_ylabel("Response")
        ax.set_title("Retardation Curve (X → US)", pad=18)
        ax.grid(alpha=0.4)
        ax.set_axisbelow(True)

        spans = self._phase_spans(retardation_records)
        if spans:
            ymin, ymax = ax.get_ylim()
            ypad = (ymax - ymin) * 0.05
            ax.set_ylim(ymin, ymax + ypad)

            for idx, (start, end, label) in enumerate(spans):
                if idx % 2 == 0:
                    ax.axvspan(
                        start,
                        end - 1,
                        color="#d0d0d0",
                        alpha=0.8,
                        zorder=1
                    )

                if start > 0:
                    ax.axvline(
                        x=start - 0.5,
                        color="#333",
                        linestyle="--",
                        linewidth=1.2,
                        zorder=2
                    )

                mid = (start + end - 1) / 2
                ax.text(
                    mid,
                    1.02,
                    label,
                    ha="center",
                    va="bottom",
                    fontsize=9,
                    color="#222",
                    transform=ax.get_xaxis_transform()
                )

    def save(self, path) -> None:
        if self.fig is None:
            raise RuntimeError("RetardationCurvePlot.render() must be called before save()")

        self.fig.savefig(path)
        plt.close(self.fig)
