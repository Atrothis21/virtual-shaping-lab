"""Executable measurement analysis operators (MVP set)."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Mapping, Sequence

from virtual_shaping_lab.vsl.contracts import TrialRecord
from virtual_shaping_lab.vsl.measurement.output import AnalysisOutput


def _coerce_record(record: TrialRecord | Mapping[str, Any]) -> dict[str, Any]:
    if isinstance(record, TrialRecord):
        return {
            "trial_index": int(record.trial_index),
            "reward": float(record.outcome.reward),
            "action": record.action.value,
            "task_input": {
                "stimuli": dict(record.task_input.stimuli),
                "available_actions": tuple(record.task_input.available_actions),
            },
            "metadata": dict(record.metadata),
        }
    if not isinstance(record, Mapping):
        raise ValueError("Analysis operators require TrialRecord or mapping records.")
    trial_index = int(record.get("trial_index", 0))
    reward = float(record.get("reward", 0.0))
    action = record.get("action")
    task_input = record.get("task_input", {})
    if not isinstance(task_input, Mapping):
        task_input = {}
    metadata = record.get("metadata", {})
    if not isinstance(metadata, Mapping):
        metadata = {}
    return {
        "trial_index": trial_index,
        "reward": reward,
        "action": action,
        "task_input": {
            "stimuli": dict(task_input.get("stimuli", {})) if isinstance(task_input.get("stimuli", {}), Mapping) else {},
            "available_actions": tuple(task_input.get("available_actions", ())),
        },
        "metadata": dict(metadata),
    }


def _coerce_records(records: Sequence[TrialRecord | Mapping[str, Any]]) -> list[dict[str, Any]]:
    if not isinstance(records, Sequence):
        raise ValueError("records must be a sequence.")
    return [_coerce_record(record) for record in records]


def _safe_entropy(probabilities: Mapping[Any, Any]) -> float:
    entropy = 0.0
    for value in probabilities.values():
        try:
            p = float(value)
        except (TypeError, ValueError):
            continue
        if p > 0.0:
            entropy -= p * math.log(p)
    return entropy


@dataclass(frozen=True)
class LearningCurveBasicAnalysisOperator:
    """Compute basic response/reward progression metrics."""

    slot: str = "M_analysis"
    variant: str = "learning_curve_basic"

    def analyze(
        self,
        *,
        records: Sequence[TrialRecord | Mapping[str, Any]],
        metadata: Mapping[str, Any] | None = None,
    ) -> AnalysisOutput:
        _ = metadata
        rows = _coerce_records(records)
        rewards = [float(row["reward"]) for row in rows]
        response_flags = [1.0 if row["action"] is not None else 0.0 for row in rows]
        cumulative_rewards: list[float] = []
        total = 0.0
        for reward in rewards:
            total += reward
            cumulative_rewards.append(total)
        metrics = {
            "trial_count": len(rows),
            "mean_reward": (sum(rewards) / len(rewards)) if rewards else 0.0,
            "response_rate": (sum(response_flags) / len(response_flags)) if response_flags else 0.0,
            "cumulative_reward_curve": cumulative_rewards,
            "reward_curve": rewards,
        }
        return AnalysisOutput(metrics=metrics, metadata={"variant": self.variant, "slot": self.slot})


@dataclass(frozen=True)
class PredictionErrorDiagnosticsAnalysisOperator:
    """Compute prediction-error summary metrics from record metadata."""

    slot: str = "M_analysis"
    variant: str = "prediction_error_diagnostics"

    def analyze(
        self,
        *,
        records: Sequence[TrialRecord | Mapping[str, Any]],
        metadata: Mapping[str, Any] | None = None,
    ) -> AnalysisOutput:
        _ = metadata
        rows = _coerce_records(records)
        errors: list[float] = []
        for row in rows:
            raw = row["metadata"].get("prediction_error")
            try:
                if raw is not None:
                    errors.append(float(raw))
            except (TypeError, ValueError):
                continue
        metrics = {
            "trial_count": len(rows),
            "prediction_error_curve": errors,
            "mean_prediction_error": (sum(errors) / len(errors)) if errors else 0.0,
            "mean_abs_prediction_error": (sum(abs(err) for err in errors) / len(errors)) if errors else 0.0,
        }
        return AnalysisOutput(metrics=metrics, metadata={"variant": self.variant, "slot": self.slot})


@dataclass(frozen=True)
class PolicyDiagnosticsAnalysisOperator:
    """Compute policy diagnostics from policy trace payloads."""

    slot: str = "M_analysis"
    variant: str = "policy_diagnostics"

    def analyze(
        self,
        *,
        records: Sequence[TrialRecord | Mapping[str, Any]],
        metadata: Mapping[str, Any] | None = None,
    ) -> AnalysisOutput:
        _ = metadata
        rows = _coerce_records(records)
        entropies: list[float] = []
        action_counts: dict[str, int] = {}
        for row in rows:
            policy_traces = row["metadata"].get("policy_traces", {})
            if not isinstance(policy_traces, Mapping):
                continue
            probs = policy_traces.get("action_probabilities", {})
            if isinstance(probs, Mapping):
                entropies.append(_safe_entropy(probs))
            action = policy_traces.get("action", row["action"])
            if action is not None:
                key = str(action)
                action_counts[key] = action_counts.get(key, 0) + 1
        metrics = {
            "trial_count": len(rows),
            "policy_entropy_curve": entropies,
            "mean_policy_entropy": (sum(entropies) / len(entropies)) if entropies else 0.0,
            "action_counts": {key: action_counts[key] for key in sorted(action_counts.keys())},
        }
        return AnalysisOutput(metrics=metrics, metadata={"variant": self.variant, "slot": self.slot})


@dataclass(frozen=True)
class BlockingDiagnosticsAnalysisOperator:
    """Compute simple cue-level reward diagnostics for blocking signatures."""

    slot: str = "M_analysis"
    variant: str = "blocking_diagnostics"

    def analyze(
        self,
        *,
        records: Sequence[TrialRecord | Mapping[str, Any]],
        metadata: Mapping[str, Any] | None = None,
    ) -> AnalysisOutput:
        _ = metadata
        rows = _coerce_records(records)
        cue_totals: dict[str, dict[str, float]] = {}
        for row in rows:
            reward = float(row["reward"])
            protocol_traces = row["metadata"].get("protocol_traces", {})
            emission = protocol_traces.get("emission", {}) if isinstance(protocol_traces, Mapping) else {}
            if not isinstance(emission, Mapping):
                emission = {}
            stimulus = emission.get("stimulus")
            if not isinstance(stimulus, Mapping):
                stimulus = row["task_input"].get("stimuli", {})
            if not isinstance(stimulus, Mapping):
                stimulus = {}
            for cue in sorted(stimulus.keys(), key=str):
                cue_key = str(cue)
                aggregate = cue_totals.setdefault(cue_key, {"reward_total": 0.0, "count": 0.0})
                aggregate["reward_total"] += reward
                aggregate["count"] += 1.0

        cue_means: dict[str, float] = {}
        for cue in sorted(cue_totals.keys()):
            count = cue_totals[cue]["count"]
            cue_means[cue] = (cue_totals[cue]["reward_total"] / count) if count else 0.0

        metrics = {
            "trial_count": len(rows),
            "cue_reward_mean": cue_means,
            "cue_count": {cue: int(cue_totals[cue]["count"]) for cue in sorted(cue_totals.keys())},
        }
        return AnalysisOutput(metrics=metrics, metadata={"variant": self.variant, "slot": self.slot})
