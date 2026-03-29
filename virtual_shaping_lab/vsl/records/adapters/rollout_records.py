"""Rollout-to-record adapters for V3 environment stepping."""

from __future__ import annotations

from typing import Any

from virtual_shaping_lab.vsl.environment.contracts import EnvironmentStep
from virtual_shaping_lab.vsl.records import RolloutRecord


def _extract_learner_traces(metadata: dict[str, Any]) -> dict[str, Any] | None:
    learner = metadata.get("learner")
    if not isinstance(learner, dict):
        return None
    traces = {
        "v": learner.get("prediction"),
        "delta": learner.get("error"),
        "theta": learner.get("update_features") if isinstance(learner.get("update_features"), dict) else {},
        "attention": learner.get("attention_state") if isinstance(learner.get("attention_state"), dict) else {},
        "memory": learner.get("eligibility_state") if isinstance(learner.get("eligibility_state"), dict) else {},
    }
    return traces


def step_to_rollout_record(
    step: EnvironmentStep,
    *,
    schema_version: str = "v1",
    rollout_id: str | None = None,
    episode_id: int | None = None,
) -> RolloutRecord:
    """Convert an EnvironmentStep into the locked RolloutRecord schema."""
    segment_index = None
    if isinstance(step.metadata, dict):
        raw_segment_index = step.metadata.get("segment_index")
        if raw_segment_index is not None:
            try:
                segment_index = int(raw_segment_index)
            except (TypeError, ValueError):
                segment_index = None
    normalized_metadata = dict(step.metadata)
    learner_traces = _extract_learner_traces(normalized_metadata)
    if isinstance(learner_traces, dict):
        normalized_metadata["learner_traces"] = learner_traces
    return RolloutRecord(
        schema_version=schema_version,
        rollout_id=rollout_id,
        episode_id=episode_id,
        segment_index=segment_index,
        step_index=int(step.step_index),
        segment_key=step.segment_key,
        protocol=step.protocol,
        trial_type=step.trial_type,
        trial_index=int(step.trial_index),
        action=step.action,
        stimulus=dict(step.stimulus),
        reward=float(step.reward),
        done=bool(step.done),
        trial_state=step.trial_state.to_dict() if step.trial_state is not None else None,
        termination=step.termination.to_dict(),
        metadata=normalized_metadata,
    )


def rollout_records_to_dict(records: list[RolloutRecord | dict[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for record in records:
        if isinstance(record, RolloutRecord):
            out.append(record.to_dict())
        else:
            out.append(dict(record))
    return out
