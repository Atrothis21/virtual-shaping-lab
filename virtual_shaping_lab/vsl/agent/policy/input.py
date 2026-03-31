"""Typed policy decision input boundary for executable policy operators."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping

from virtual_shaping_lab.vsl.contracts import TaskInput

_DISALLOWED_POLICY_INPUT_KEYS = {
    "raw_stimulus",
    "stimuli",
    "task_input",
    "reward",
    "outcome",
    "prediction_error",
    "delta",
}


def _copy_dict(value: Mapping[str, Any] | None) -> dict[str, Any]:
    if value is None:
        return {}
    return dict(value)


@dataclass(frozen=True)
class PolicyInput:
    """Canonical decision-context transport for policy selection."""

    observation_features: list[float] = field(default_factory=list)
    observation_feature_names: list[str] = field(default_factory=list)
    representation: Any = None
    context_state: Any = None
    generalized_state: Any = None
    prediction: float | None = None
    action_values: dict[Any, float] = field(default_factory=dict)
    available_actions: tuple[Any, ...] = field(default_factory=tuple)
    trial_state: dict[str, Any] = field(default_factory=dict)
    agent_state: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.observation_features, list):
            raise ValueError("PolicyInput.observation_features must be a list.")
        if not all(isinstance(value, (int, float)) for value in self.observation_features):
            raise ValueError("PolicyInput.observation_features must contain numeric values.")
        if not isinstance(self.observation_feature_names, list):
            raise ValueError("PolicyInput.observation_feature_names must be a list.")
        if not all(isinstance(name, str) for name in self.observation_feature_names):
            raise ValueError("PolicyInput.observation_feature_names must contain strings.")
        if len(self.observation_feature_names) not in {0, len(self.observation_features)}:
            raise ValueError("PolicyInput.observation_feature_names must be empty or match features length.")
        if not isinstance(self.action_values, dict):
            raise ValueError("PolicyInput.action_values must be an object.")
        if not isinstance(self.trial_state, dict):
            raise ValueError("PolicyInput.trial_state must be an object.")
        if not isinstance(self.agent_state, dict):
            raise ValueError("PolicyInput.agent_state must be an object.")
        if not isinstance(self.metadata, dict):
            raise ValueError("PolicyInput.metadata must be an object.")
        forbidden = sorted(_DISALLOWED_POLICY_INPUT_KEYS.intersection(self.metadata.keys()))
        if forbidden:
            joined = ", ".join(forbidden)
            raise ValueError(f"PolicyInput.metadata contains disallowed raw/boundary keys: {joined}.")

        object.__setattr__(self, "observation_features", [float(v) for v in self.observation_features])
        object.__setattr__(self, "observation_feature_names", [str(v) for v in self.observation_feature_names])
        object.__setattr__(self, "action_values", {k: float(v) for k, v in self.action_values.items()})
        object.__setattr__(self, "available_actions", tuple(self.available_actions))
        object.__setattr__(self, "trial_state", dict(self.trial_state))
        object.__setattr__(self, "agent_state", dict(self.agent_state))
        object.__setattr__(self, "metadata", dict(self.metadata))

    def to_mapping(self) -> dict[str, Any]:
        return {
            "observation_features": list(self.observation_features),
            "observation_feature_names": list(self.observation_feature_names),
            "representation": self.representation,
            "context_state": self.context_state,
            "generalized_state": self.generalized_state,
            "prediction": self.prediction,
            "action_values": dict(self.action_values),
            "available_actions": list(self.available_actions),
            "trial_state": dict(self.trial_state),
            "agent_state": dict(self.agent_state),
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_mapping(cls, data: Mapping[str, Any]) -> "PolicyInput":
        return cls(
            observation_features=list(data.get("observation_features", []) or []),
            observation_feature_names=list(data.get("observation_feature_names", []) or []),
            representation=data.get("representation"),
            context_state=data.get("context_state"),
            generalized_state=data.get("generalized_state"),
            prediction=data.get("prediction"),
            action_values=dict(data.get("action_values", {}) or {}),
            available_actions=tuple(data.get("available_actions", ()) or ()),
            trial_state=dict(data.get("trial_state", {}) or {}),
            agent_state=dict(data.get("agent_state", {}) or {}),
            metadata=dict(data.get("metadata", {}) or {}),
        )


def _extract_prediction_scalar(prediction: Any) -> float | None:
    if prediction is None:
        return None
    if isinstance(prediction, (int, float)):
        return float(prediction)
    if isinstance(prediction, Mapping):
        value = prediction.get("state_value")
        return float(value) if isinstance(value, (int, float)) else None
    value = getattr(prediction, "state_value", None)
    return float(value) if isinstance(value, (int, float)) else None


def _extract_action_values(prediction: Any) -> dict[Any, float]:
    if prediction is None:
        return {}
    if isinstance(prediction, Mapping):
        raw = prediction.get("action_values", {})
    else:
        raw = getattr(prediction, "action_values", {})
    if not isinstance(raw, Mapping):
        return {}
    return {action: float(value) for action, value in raw.items() if isinstance(value, (int, float))}


def build_policy_input(
    *,
    task_input: TaskInput,
    observation_output: Any,
    prediction: Any = None,
    available_actions: tuple[Any, ...] | None = None,
    trial_state: Mapping[str, Any] | None = None,
    agent_state: Mapping[str, Any] | None = None,
    metadata: Mapping[str, Any] | None = None,
) -> PolicyInput:
    """Build canonical PolicyInput from typed boundary and subsystem outputs."""
    if not isinstance(task_input, TaskInput):
        raise TypeError("task_input must be TaskInput.")

    features = list(getattr(observation_output, "features", []) or [])
    feature_names = list(getattr(observation_output, "feature_names", []) or [])
    representation = getattr(observation_output, "representation", None)
    context_state = getattr(observation_output, "context_state", None)
    generalized_state = getattr(observation_output, "generalized_state", None)

    chosen_actions = tuple(available_actions) if available_actions is not None else tuple(task_input.available_actions)

    merged_meta = _copy_dict(metadata)
    merged_meta.setdefault("source", "task_observation_prediction")
    merged_meta.setdefault("task_time", task_input.t)
    merged_meta.setdefault("task_phase", task_input.phase)

    return PolicyInput(
        observation_features=features,
        observation_feature_names=feature_names,
        representation=representation,
        context_state=context_state,
        generalized_state=generalized_state,
        prediction=_extract_prediction_scalar(prediction),
        action_values=_extract_action_values(prediction),
        available_actions=chosen_actions,
        trial_state=dict(trial_state or {}),
        agent_state=dict(agent_state or {}),
        metadata=merged_meta,
    )

