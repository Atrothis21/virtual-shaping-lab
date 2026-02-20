# analysis/visualizations/operant.py

import matplotlib.pyplot as plt
from analysis.visualizations.base import Visualization


class CumulativeResponsePlot(Visualization):
    """
    Plot cumulative responses over trials.
    """

    name = "cumulative_response_plot"

    def __init__(self):
        self.fig = None

    def render(self, records, metrics=None, **kwargs) -> None:
        if records:
            data = []
            total = 0
            for r in records:
                if r.get("action") is not None:
                    total += 1
                data.append(total)
        else:
            data = metrics.get("cumulative_responses") if metrics else None

        if data is None:
            raise KeyError(
                "CumulativeResponsePlot requires records or metric 'cumulative_responses'"
            )

        self.fig, ax = plt.subplots()
        ax.plot(data)
        ax.set_xlabel("Trial")
        ax.set_ylabel("Cumulative Responses")
        ax.set_title("Cumulative Responses Over Time")

    def save(self, path) -> None:
        if self.fig is None:
            raise RuntimeError("CumulativeResponsePlot.render() must be called before save()")

        self.fig.savefig(path)
        plt.close(self.fig)


class CumulativeRewardPlot(Visualization):
    """
    Plot cumulative rewards over trials.
    """

    name = "cumulative_reward_plot"

    def __init__(self):
        self.fig = None

    def render(self, records, metrics=None, **kwargs) -> None:
        if records:
            data = []
            total = 0.0
            for r in records:
                total += float(r.get("reward", 0.0))
                data.append(total)
        else:
            data = metrics.get("cumulative_rewards") if metrics else None

        if data is None:
            raise KeyError(
                "CumulativeRewardPlot requires records or metric 'cumulative_rewards'"
            )

        self.fig, ax = plt.subplots()
        ax.plot(data)
        ax.set_xlabel("Trial")
        ax.set_ylabel("Cumulative Reward")
        ax.set_title("Cumulative Reward Over Time")

    def save(self, path) -> None:
        if self.fig is None:
            raise RuntimeError("CumulativeRewardPlot.render() must be called before save()")

        self.fig.savefig(path)
        plt.close(self.fig)
