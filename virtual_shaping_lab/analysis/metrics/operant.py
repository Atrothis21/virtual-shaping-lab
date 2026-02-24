# analysis/metrics/operant.py

from typing import Any, Dict, List

from analysis.metrics.base import Metric, TimeSeriesMetric


class CumulativeResponses(TimeSeriesMetric):
    """
    Cumulative number of responses over trials.

    Each operant trial produces exactly one response.
    """

    name = "cumulative_responses"

    def _compute_series(
        self,
        records: List[Dict[str, Any]]
    ) -> List[int]:
        cumulative = []
        total = 0

        for _ in records:
            total += 1
            cumulative.append(total)

        return cumulative


class CumulativeRewards(TimeSeriesMetric):
    """
    Cumulative sum of rewards over trials.
    """

    name = "cumulative_rewards"

    def _compute_series(
        self,
        records: List[Dict[str, Any]]
    ) -> List[float]:
        cumulative = []
        total = 0.0

        for record in records:
            total += record.get("reward", 0.0)
            cumulative.append(total)

        return cumulative


def _phase_label(record: Dict[str, Any]) -> str:
    return (
        str(record.get("subphase_name"))
        if record.get("subphase_name") is not None
        else str(
            record.get("phase_name")
            if record.get("phase_name") is not None
            else record.get("phase", "unknown")
        )
    )


def _action_label(record: Dict[str, Any]) -> str:
    raw = record.get("action_raw")
    if raw is not None:
        return str(raw)
    label = record.get("action_label")
    if label is not None:
        return str(label)
    action = record.get("action")
    return str(action) if action is not None else "none"


class OutcomeTypeCounts(Metric):
    """
    Count reinforcement/extinction/punishment outcomes.
    """

    name = "outcome_type_counts"

    def compute(self, records: List[Dict[str, Any]]) -> Dict[str, int]:
        counts = {
            "reinforcement": 0,
            "extinction": 0,
            "punishment": 0,
        }
        for record in records:
            reward = float(record.get("reward", 0.0))
            outcome = record.get("outcome_type")
            if outcome not in counts:
                if reward > 0:
                    outcome = "reinforcement"
                elif reward < 0:
                    outcome = "punishment"
                else:
                    outcome = "extinction"
            counts[outcome] += 1
        return counts


class ActionCounts(Metric):
    """
    Count emitted actions across records.
    """

    name = "action_counts"

    def compute(self, records: List[Dict[str, Any]]) -> Dict[str, int]:
        counts: Dict[str, int] = {}
        for record in records:
            label = _action_label(record)
            counts[label] = counts.get(label, 0) + 1
        return dict(sorted(counts.items(), key=lambda kv: kv[0]))


class PhaseRewardSummary(Metric):
    """
    Per-phase reward summary statistics.
    """

    name = "phase_reward_summary"

    def compute(self, records: List[Dict[str, Any]]) -> Dict[str, Dict[str, float]]:
        buckets: Dict[str, List[float]] = {}
        for record in records:
            phase = _phase_label(record)
            buckets.setdefault(phase, []).append(float(record.get("reward", 0.0)))

        summary: Dict[str, Dict[str, float]] = {}
        for phase, rewards in buckets.items():
            n = len(rewards)
            summary[phase] = {
                "n_trials": float(n),
                "total_reward": float(sum(rewards)),
                "mean_reward": float(sum(rewards) / n) if n else 0.0,
                "reinforcement_rate": float(sum(1 for r in rewards if r > 0) / n) if n else 0.0,
                "punishment_rate": float(sum(1 for r in rewards if r < 0) / n) if n else 0.0,
            }
        return summary
