"""Canonical runtime seam for policy execution."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Sequence

from virtual_shaping_lab.vsl.agent.policy import (
    ExecutablePolicyPreset,
    PolicyInput,
    PolicyOutput,
    build_executable_policy_preset,
    build_policy_input,
)
from virtual_shaping_lab.vsl.contracts import TaskInput


@dataclass(frozen=True)
class _ObservationAdapterInput:
    features: list[float]
    feature_names: list[str]
    representation: Any = None
    context_state: Any = None
    generalized_state: Any = None


def _normalize_available_actions(
    available_actions: Any,
    *,
    fallback: tuple[Any, ...] = (),
) -> tuple[Any, ...]:
    if available_actions is None:
        return tuple(fallback)
    if isinstance(available_actions, tuple):
        return available_actions
    if isinstance(available_actions, Sequence) and not isinstance(available_actions, (str, bytes, bytearray)):
        return tuple(available_actions)
    return (available_actions,)


def _coerce_task_input(task_input: TaskInput | Mapping[str, Any] | None, *, available_actions: tuple[Any, ...]) -> TaskInput:
    if isinstance(task_input, TaskInput):
        return task_input
    if isinstance(task_input, Mapping):
        payload = dict(task_input)
        raw_actions = payload.get("available_actions")
        normalized_actions = _normalize_available_actions(raw_actions, fallback=available_actions)
        return TaskInput(
            stimuli=dict(payload.get("stimuli", {}) or {}),
            context=payload.get("context"),
            t=payload.get("t"),
            phase=payload.get("phase"),
            available_actions=normalized_actions,
            metadata=dict(payload.get("metadata", {}) or {}),
        )
    return TaskInput(stimuli={}, available_actions=tuple(available_actions))


def _coerce_observation_output(observation_output: Any) -> _ObservationAdapterInput:
    if observation_output is None:
        return _ObservationAdapterInput(features=[], feature_names=[])
    features = list(getattr(observation_output, "features", []) or [])
    feature_names = list(getattr(observation_output, "feature_names", []) or [])
    return _ObservationAdapterInput(
        features=[float(v) for v in features],
        feature_names=[str(v) for v in feature_names],
        representation=getattr(observation_output, "representation", None),
        context_state=getattr(observation_output, "context_state", None),
        generalized_state=getattr(observation_output, "generalized_state", None),
    )


@dataclass
class RuntimePolicyAdapter:
    """Runtime adapter that routes action selection through one canonical policy seam."""

    preset_name: str
    executable: ExecutablePolicyPreset

    def step(
        self,
        *,
        task_input: TaskInput | Mapping[str, Any] | None = None,
        observation_output: Any = None,
        prediction: Any = None,
        available_actions: Any = None,
        trial_state: Mapping[str, Any] | None = None,
        agent_state: Mapping[str, Any] | None = None,
        metadata: Mapping[str, Any] | None = None,
        rng: Any | None = None,
    ) -> PolicyOutput:
        normalized_actions = _normalize_available_actions(available_actions)
        normalized_task_input = _coerce_task_input(task_input, available_actions=normalized_actions)
        if not normalized_actions:
            normalized_actions = tuple(normalized_task_input.available_actions)

        policy_input: PolicyInput = build_policy_input(
            task_input=normalized_task_input,
            observation_output=_coerce_observation_output(observation_output),
            prediction=prediction,
            available_actions=normalized_actions,
            trial_state=dict(trial_state or {}),
            agent_state=dict(agent_state or {}),
            metadata={
                **dict(metadata or {}),
                "runtime_policy": {
                    "preset_name": self.preset_name,
                    "normalization": "runtime_available_actions_v1",
                },
            },
        )
        return self.executable.policy_operator.select(
            policy_input=policy_input,
            available_actions=tuple(policy_input.available_actions),
            rng=rng,
            metadata=dict(policy_input.metadata),
        )


def build_runtime_policy_adapter(
    *,
    preset_name: str = "no_policy",
    epsilon: float = 0.1,
    temperature: float = 1.0,
    tie_break_rule: str = "stable_lexicographic",
) -> RuntimePolicyAdapter:
    executable = build_executable_policy_preset(
        preset_name,
        epsilon=epsilon,
        temperature=temperature,
        tie_break_rule=tie_break_rule,
    )
    return RuntimePolicyAdapter(
        preset_name=preset_name,
        executable=executable,
    )

