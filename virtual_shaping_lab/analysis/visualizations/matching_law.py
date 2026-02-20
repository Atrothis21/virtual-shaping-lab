# analysis/visualizations/matching_law.py

import matplotlib.pyplot as plt
from analysis.visualizations.base import Visualization


class MatchingLawPlot(Visualization):
    """
    Plot response proportion vs reinforcement proportion for matching law.
    """

    name = "matching_law_plot"

    def __init__(self):
        self.fig = None

    def render(self, records, metrics=None, **kwargs) -> None:
        responses_left = 0
        responses_right = 0
        rewards_left = 0.0
        rewards_right = 0.0

        for r in records or []:
            action = r.get("action")
            reward = float(r.get("reward", 0.0))
            if action == 0:
                responses_left += 1
                if reward > 0:
                    rewards_left += reward
            elif action == 1:
                responses_right += 1
                if reward > 0:
                    rewards_right += reward

        total_responses = responses_left + responses_right
        total_rewards = rewards_left + rewards_right

        response_prop = (responses_left / total_responses) if total_responses else 0.0
        reward_prop = (rewards_left / total_rewards) if total_rewards else 0.0

        self.fig, ax = plt.subplots()
        ax.scatter([reward_prop], [response_prop], s=80, color="#2563eb")
        ax.plot([0, 1], [0, 1], linestyle="--", color="#666", alpha=0.6)
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.set_xlabel("Reinforcement Proportion (Left / Total)")
        ax.set_ylabel("Response Proportion (Left / Total)")
        ax.set_title("Matching Law")
        ax.grid(alpha=0.3)

    def save(self, path) -> None:
        if self.fig is None:
            raise RuntimeError("MatchingLawPlot.render() must be called before save()")
        self.fig.savefig(path)
        plt.close(self.fig)
