"""Rollout-to-record adapters for V3 environment stepping."""

from __future__ import annotations

from typing import Any

from virtual_shaping_lab.vsl.environment.contracts import EnvironmentStep
from virtual_shaping_lab.vsl.records import RolloutRecord


def _stable_copy(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(k): _stable_copy(v) for k, v in sorted(value.items(), key=lambda item: str(item[0]))}
    if isinstance(value, list):
        return [_stable_copy(v) for v in value]
    if isinstance(value, tuple):
        return [_stable_copy(v) for v in value]
    return value


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


def _extract_observation_traces(metadata: dict[str, Any]) -> dict[str, Any] | None:
    observation = metadata.get("observation")
    if not isinstance(observation, dict):
        return None
    output = observation.get("output")
    if not isinstance(output, dict):
        return None
    traces = {
        "representation": output.get("representation"),
        "context_state": output.get("context_state"),
        "generalized_state": output.get("generalized_state"),
        "features": list(output.get("features", []) or []),
        "feature_names": list(output.get("feature_names", []) or []),
        "provenance": {},
    }
    out_meta = output.get("metadata")
    if isinstance(out_meta, dict):
        runtime_observation = out_meta.get("runtime_observation")
        if isinstance(runtime_observation, dict):
            traces["provenance"]["runtime_observation"] = dict(runtime_observation)
        stage_traces = out_meta.get("stage_traces")
        if isinstance(stage_traces, dict):
            traces["provenance"]["stage_traces"] = dict(stage_traces)
    return traces


def _extract_policy_traces(metadata: dict[str, Any]) -> dict[str, Any] | None:
    policy = metadata.get("policy")
    if not isinstance(policy, dict):
        return None
    traces = {
        "action": policy.get("action"),
        "available_actions": list(policy.get("available_actions", []) or []),
        "action_scores": dict(policy.get("action_scores", {}) or {}),
        "action_probabilities": dict(policy.get("action_probabilities", {}) or {}),
        "provenance": {},
    }
    policy_metadata = policy.get("metadata")
    if isinstance(policy_metadata, dict):
        traces["provenance"] = dict(policy_metadata)
    return traces


def _extract_protocol_traces(metadata: dict[str, Any]) -> dict[str, Any] | None:
    protocol = metadata.get("protocol")
    if not isinstance(protocol, dict):
        return None

    emission = protocol.get("emission")
    consequence = protocol.get("consequence")
    advance = protocol.get("advance")
    stop = protocol.get("stop")

    traces = {
        "emission": _stable_copy(emission) if isinstance(emission, dict) else {},
        "consequence": _stable_copy(consequence) if isinstance(consequence, dict) else {},
        "advance": _stable_copy(advance) if isinstance(advance, dict) else {},
        "stop": _stable_copy(stop) if isinstance(stop, dict) else {},
        "provenance": {
            "preset_name": protocol.get("preset_name"),
            "pipeline_order": list(protocol.get("pipeline_order", []) or []),
        },
        "timing": {},
    }

    if isinstance(traces["advance"], dict):
        if "t" in traces["advance"]:
            traces["timing"]["t"] = traces["advance"].get("t")
        if "phase_step" in traces["advance"]:
            traces["timing"]["phase_step"] = traces["advance"].get("phase_step")
        if "dt_s" in traces["advance"]:
            traces["timing"]["dt_s"] = traces["advance"].get("dt_s")

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
    observation_traces = _extract_observation_traces(normalized_metadata)
    if isinstance(observation_traces, dict):
        normalized_metadata["observation_traces"] = observation_traces
    policy_traces = _extract_policy_traces(normalized_metadata)
    if isinstance(policy_traces, dict):
        normalized_metadata["policy_traces"] = policy_traces
    protocol_traces = _extract_protocol_traces(normalized_metadata)
    if isinstance(protocol_traces, dict):
        normalized_metadata["protocol_traces"] = protocol_traces
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
