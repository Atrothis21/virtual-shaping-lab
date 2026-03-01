"""Record view adapters for analysis."""

from __future__ import annotations

from typing import Any


def trial_view(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Return trial-level rows from mixed record streams."""
    rows: list[dict[str, Any]] = []
    for row in records:
        if row.get("tick") is None:
            rows.append(dict(row))
    return rows


def tick_view(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Return tick-level rows from mixed record streams."""
    rows: list[dict[str, Any]] = []
    for row in records:
        if row.get("tick") is not None:
            rows.append(dict(row))
    return rows


def aggregate_ticks_to_trials(ticks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Aggregate tick records into trial summaries.

    Rules:
    - one output row per trial
    - reward is summed over ticks
    - response/action is last non-null action
    - prediction uses last available prediction (if present)
    - context/phase metadata copied from first tick row
    """
    grouped: dict[Any, list[dict[str, Any]]] = {}
    for row in ticks:
        key = row.get("trial")
        grouped.setdefault(key, []).append(row)

    summaries: list[dict[str, Any]] = []
    for trial_id in sorted(grouped.keys(), key=lambda x: (x is None, x)):
        rows = sorted(grouped[trial_id], key=lambda r: int(r.get("tick", 0)))
        first = rows[0]
        total_reward = float(sum(float(r.get("reward", 0.0) or 0.0) for r in rows))

        last_action = None
        for r in rows:
            if r.get("action") is not None:
                last_action = r.get("action")

        last_prediction = None
        for r in rows:
            if r.get("prediction") is not None:
                last_prediction = r.get("prediction")

        summaries.append(
            {
                "phase": first.get("phase"),
                "phase_name": first.get("phase_name"),
                "protocol_name": first.get("protocol_name"),
                "unit_path": first.get("unit_path"),
                "subphase": first.get("subphase"),
                "subphase_name": first.get("subphase_name"),
                "trial": trial_id,
                "reward": total_reward,
                "action": last_action,
                "response": last_action,
                "prediction": last_prediction,
                "context": first.get("context"),
                "tick_count": len(rows),
                "t_s_start": rows[0].get("t_s"),
                "t_s_end": rows[-1].get("t_s"),
            }
        )
    return summaries
