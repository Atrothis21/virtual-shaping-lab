import matplotlib.pyplot as plt

from analysis.visualizations.base import Visualization


def _phase_label(record):
    if record.get("subphase_name") is not None:
        return str(record.get("subphase_name"))
    if record.get("phase_name") is not None:
        return str(record.get("phase_name"))
    return str(record.get("phase", "unknown"))


def _action_label(record):
    if record.get("action_raw") is not None:
        return str(record.get("action_raw"))
    if record.get("action_label") is not None:
        return str(record.get("action_label"))
    action = record.get("action")
    return str(action) if action is not None else "none"


class RewardTimeSeriesPlot(Visualization):
    """
    Trial-wise reward with moving average to reveal schedule regimes.
    """

    name = "reward_time_series_plot"

    def __init__(self):
        self.fig = None

    def render(self, records, metrics=None, **kwargs):
        rewards = [float(r.get("reward", 0.0)) for r in (records or [])]
        if not rewards and metrics:
            rewards = list(metrics.get("reward_time_series", []))
        if not rewards:
            raise ValueError("RewardTimeSeriesPlot requires reward records or reward_time_series metric.")

        window = max(1, min(20, len(rewards)))
        moving = []
        for i in range(len(rewards)):
            start = max(0, i - window + 1)
            vals = rewards[start : i + 1]
            moving.append(sum(vals) / len(vals))

        self.fig, ax = plt.subplots()
        ax.plot(rewards, alpha=0.35, linewidth=1.0, label="trial reward")
        ax.plot(moving, linewidth=2.0, label=f"moving avg ({window})")
        ax.set_xlabel("Trial")
        ax.set_ylabel("Reward")
        ax.set_title("Reward Time Series")
        ax.grid(alpha=0.3)
        ax.legend()

    def save(self, path):
        if self.fig is None:
            raise RuntimeError("RewardTimeSeriesPlot.render() must be called before save().")
        self.fig.savefig(path)
        plt.close(self.fig)


class ActionDistributionPlot(Visualization):
    """
    Action frequency distribution.
    """

    name = "action_distribution_plot"

    def __init__(self):
        self.fig = None

    def render(self, records, metrics=None, **kwargs):
        counts = {}
        for record in records or []:
            label = _action_label(record)
            counts[label] = counts.get(label, 0) + 1
        if not counts and metrics:
            counts = dict(metrics.get("action_counts", {}))
        if not counts:
            raise ValueError("ActionDistributionPlot requires action records or action_counts metric.")

        labels = list(counts.keys())
        values = [counts[k] for k in labels]

        self.fig, ax = plt.subplots()
        ax.bar(labels, values, color="#2563eb")
        ax.set_xlabel("Action")
        ax.set_ylabel("Count")
        ax.set_title("Action Distribution")
        ax.grid(axis="y", alpha=0.3)
        ax.set_axisbelow(True)

    def save(self, path):
        if self.fig is None:
            raise RuntimeError("ActionDistributionPlot.render() must be called before save().")
        self.fig.savefig(path)
        plt.close(self.fig)


class OutcomeTypeBarPlot(Visualization):
    """
    Reinforcement/extinction/punishment count summary.
    """

    name = "outcome_type_bar_plot"

    def __init__(self):
        self.fig = None

    def render(self, records, metrics=None, **kwargs):
        counts = {"reinforcement": 0, "extinction": 0, "punishment": 0}
        for record in records or []:
            reward = float(record.get("reward", 0.0))
            outcome = record.get("outcome_type")
            if outcome not in counts:
                outcome = "reinforcement" if reward > 0 else ("punishment" if reward < 0 else "extinction")
            counts[outcome] += 1

        if not any(counts.values()) and metrics:
            metric_counts = metrics.get("outcome_type_counts")
            if isinstance(metric_counts, dict):
                counts = {
                    "reinforcement": int(metric_counts.get("reinforcement", 0)),
                    "extinction": int(metric_counts.get("extinction", 0)),
                    "punishment": int(metric_counts.get("punishment", 0)),
                }

        if not any(counts.values()):
            raise ValueError("OutcomeTypeBarPlot requires records or outcome_type_counts metric.")

        labels = ["reinforcement", "extinction", "punishment"]
        values = [counts[l] for l in labels]
        colors = ["#16a34a", "#6b7280", "#dc2626"]

        self.fig, ax = plt.subplots()
        ax.bar(labels, values, color=colors)
        ax.set_xlabel("Outcome Type")
        ax.set_ylabel("Count")
        ax.set_title("Outcome-Type Distribution")
        ax.grid(axis="y", alpha=0.3)
        ax.set_axisbelow(True)

    def save(self, path):
        if self.fig is None:
            raise RuntimeError("OutcomeTypeBarPlot.render() must be called before save().")
        self.fig.savefig(path)
        plt.close(self.fig)


class PhaseRewardBarPlot(Visualization):
    """
    Mean reward per phase/subphase.
    """

    name = "phase_reward_bar_plot"

    def __init__(self):
        self.fig = None

    def render(self, records, metrics=None, **kwargs):
        summary = {}
        for record in records or []:
            label = _phase_label(record)
            summary.setdefault(label, []).append(float(record.get("reward", 0.0)))

        if not summary and metrics:
            metric_summary = metrics.get("phase_reward_summary")
            if isinstance(metric_summary, dict) and metric_summary:
                labels = list(metric_summary.keys())
                means = [float(metric_summary[k].get("mean_reward", 0.0)) for k in labels]
                self.fig, ax = plt.subplots()
                ax.bar(labels, means, color="#0ea5e9")
                ax.axhline(0.0, color="#111", linewidth=1.0, alpha=0.6)
                ax.set_xlabel("Phase")
                ax.set_ylabel("Mean Reward")
                ax.set_title("Mean Reward by Phase")
                ax.tick_params(axis="x", rotation=20)
                ax.grid(axis="y", alpha=0.3)
                ax.set_axisbelow(True)
                return

        if not summary:
            raise ValueError("PhaseRewardBarPlot requires records or phase_reward_summary metric.")

        labels = list(summary.keys())
        means = [sum(v) / len(v) if v else 0.0 for v in summary.values()]

        self.fig, ax = plt.subplots()
        ax.bar(labels, means, color="#0ea5e9")
        ax.axhline(0.0, color="#111", linewidth=1.0, alpha=0.6)
        ax.set_xlabel("Phase")
        ax.set_ylabel("Mean Reward")
        ax.set_title("Mean Reward by Phase")
        ax.tick_params(axis="x", rotation=20)
        ax.grid(axis="y", alpha=0.3)
        ax.set_axisbelow(True)

    def save(self, path):
        if self.fig is None:
            raise RuntimeError("PhaseRewardBarPlot.render() must be called before save().")
        self.fig.savefig(path)
        plt.close(self.fig)
