from typing import Dict, Any, List
import matplotlib.pyplot as plt

from analysis.visualizations.base import Visualization


class DualTimeSeriesPlot(Visualization):
    """
    Minimal dual time series plotter.

    Expects records to include:
      - series_values: {"Label A": value_or_None, "Label B": value_or_None}
      - series_labels: {"label_1": "Label A", "label_2": "Label B"} (optional)

    Plotting logic:
      - Each label gets its own line
      - Values of None are skipped
    """

    name = "dual_time_series_plot"

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

    def _resolve_label_map(self, records: List[Dict[str, Any]]) -> Dict[str, str]:
        for r in records:
            a = r.get("a_stimulus")
            b = r.get("b_stimulus")
            if a and b:
                return {"CS1": a, "CS2": b}
        return {}

    def _label_map_from_records(self, records: List[Dict[str, Any]]) -> Dict[str, str]:
        # Map CS1/CS2 → actual stimulus names if present
        for r in records:
            a = r.get("a_stimulus")
            b = r.get("b_stimulus")
            if a and b:
                return {"CS1": a, "CS2": b}
            if a and b is None:
                return {"CS1": a}

        # Map CS+/CS- → actual stimulus names if present
        cs_plus = None
        cs_minus = None
        for r in records:
            if r.get("stimulus_type") == "cs_plus" and r.get("stimulus"):
                cs_plus = r["stimulus"]
            if r.get("stimulus_type") == "cs_minus" and r.get("stimulus"):
                cs_minus = r["stimulus"]
            if cs_plus and cs_minus:
                break

        if cs_plus or cs_minus:
            return {
                "CS+": cs_plus if cs_plus else "CS+",
                "CS-": cs_minus if cs_minus else "CS-"
            }

        return {}

    @staticmethod
    def _coerce_series_values(record: Dict[str, Any]) -> Dict[str, Any] | None:
        """
        Normalize per-record series input for dual plotting.

        Differential template records can emit one-sided payloads like:
          series_values={"CS1": prediction, "CS2": None}
        for both CS+ and CS- trials. This helper reconstructs canonical
        CS+/CS- series slots from stimulus_type + prediction so two curves
        are rendered correctly.
        """
        sv = record.get("series_values")
        stim_type = record.get("stimulus_type")
        prediction = record.get("prediction")

        if isinstance(sv, dict):
            # Backward-compat normalization for one-sided CS1/CS2 template output.
            if (
                set(sv.keys()) == {"CS1", "CS2"}
                and sv.get("CS2") is None
                and stim_type in {"cs_plus", "cs_minus"}
                and prediction is not None
            ):
                return {
                    "CS+": prediction if stim_type == "cs_plus" else None,
                    "CS-": prediction if stim_type == "cs_minus" else None,
                }
            return sv

        # Synthesize series slots if explicit series payload is absent.
        if stim_type in {"cs_plus", "cs_minus"} and prediction is not None:
            return {
                "CS+": prediction if stim_type == "cs_plus" else None,
                "CS-": prediction if stim_type == "cs_minus" else None,
            }

        return None

    def render(
        self,
        records: List[Dict[str, Any]],
        metrics: Dict[str, Any],
    ) -> None:
        if not records:
            raise ValueError("DualTimeSeriesPlot received no records")

        label_map = self._label_map_from_records(records)

        # Gather series from records
        series = {}
        labels = None
        differential_mode = any(
            r.get("stimulus_type") in {"cs_plus", "cs_minus"}
            for r in records
        )

        for i, r in enumerate(records):
            sv = self._coerce_series_values(r)
            if not isinstance(sv, dict):
                continue

            if labels is None and isinstance(r.get("series_labels"), dict):
                labels = r.get("series_labels")

            for name, val in sv.items():
                if val is None:
                    continue
                canonical = label_map.get(name, name)
                series.setdefault(canonical, {"trials": [], "values": []})
                if differential_mode and canonical in {"CS+", "CS-"}:
                    x_val = len(series[canonical]["trials"])
                else:
                    x_val = i
                series[canonical]["trials"].append(x_val)
                series[canonical]["values"].append(val)

        if not series:
            raise ValueError(
                "DualTimeSeriesPlot requires series_values in records "
                "(no usable series found)"
            )

        # Normalize labels to mapped names
        if labels and label_map:
            labels = {
                "label_1": label_map.get(labels.get("label_1"), labels.get("label_1")),
                "label_2": label_map.get(labels.get("label_2"), labels.get("label_2")),
            }

        self.fig, ax = plt.subplots()

        # Preserve label order if provided
        if labels:
            ordered = [labels.get("label_1"), labels.get("label_2")]
            for name in ordered:
                if name in series:
                    ax.plot(series[name]["trials"], series[name]["values"], label=name)

            # Plot any extra series not in labels
            for name, data in series.items():
                if name not in ordered:
                    ax.plot(data["trials"], data["values"], label=name)
        else:
            for name, data in series.items():
                ax.plot(data["trials"], data["values"], label=name)

        ax.set_xlabel("Trial")
        ax.set_ylabel("Prediction")
        ax.set_title("Time Series", pad=8)
        ax.legend()
        ax.grid(alpha=0.4)
        ax.set_axisbelow(True)

        spans = self._phase_spans(records)
        if spans:
            for idx, (start, end, label) in enumerate(spans):
                if idx % 2 == 0:
                    ax.axvspan(start, end - 1, color="#d0d0d0", alpha=0.8, zorder=1)
                if start > 0:
                    ax.axvline(x=start - 0.5, color="#333", linestyle="--", linewidth=1.2, zorder=2)

            top = ax.secondary_xaxis("top")
            mids = [(s + e - 1) / 2 for (s, e, _) in spans]
            labels = [lbl for (_, _, lbl) in spans]
            top.set_xticks(mids)
            top.set_xticklabels(labels, rotation=20, ha="left", fontsize=8)
            top.tick_params(axis="x", pad=6, length=0)

    def save(self, path) -> None:
        if self.fig is None:
            raise RuntimeError("DualTimeSeriesPlot.render() must be called before save()")

        self.fig.savefig(path)
        plt.close(self.fig)
