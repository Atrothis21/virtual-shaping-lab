"""Thin compositional agent orchestrator over observation/learner/policy seams."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, Sequence

from virtual_shaping_lab.vsl.contracts import Action, Outcome, TaskInput
from virtual_shaping_lab.vsl.runtime.learner_adapter import RuntimeLearnerAdapter, build_runtime_learner_adapter
from virtual_shaping_lab.vsl.runtime.observation_adapter import (
    RuntimeObservationAdapter,
    build_runtime_observation_adapter,
)
from virtual_shaping_lab.vsl.runtime.policy_adapter import RuntimePolicyAdapter, build_runtime_policy_adapter

from .learning import LearnerStepResult, PredictionOutput
from .observation import ObservationOutput, ObservationStepResult
from .policy import PolicyOutput


def _coerce_task_input(value: TaskInput | Mapping[str, Any]) -> TaskInput:
    if isinstance(value, TaskInput):
        return value
    if isinstance(value, Mapping):
        payload = dict(value)
        return TaskInput(
            stimuli=dict(payload.get("stimuli", {}) or {}),
            context=payload.get("context"),
            t=payload.get("t"),
            phase=payload.get("phase"),
            available_actions=tuple(payload.get("available_actions", ()) or ()),
            metadata=dict(payload.get("metadata", {}) or {}),
        )
    raise TypeError("task_input must be TaskInput or object payload.")


def _coerce_action(value: Action | Any) -> Action:
    if isinstance(value, Action):
        return value
    return Action(value=value)


def _coerce_outcome(value: Outcome | Mapping[str, Any]) -> Outcome:
    if isinstance(value, Outcome):
        return value
    if isinstance(value, Mapping):
        payload = dict(value)
        return Outcome(
            reward=float(payload.get("reward", 0.0)),
            next_stimuli=dict(payload.get("next_stimuli", {}) or {}),
            terminated=bool(payload.get("terminated", False)),
            truncated=bool(payload.get("truncated", False)),
            metadata=dict(payload.get("metadata", {}) or {}),
        )
    raise TypeError("outcome must be Outcome or object payload.")


def _coerce_observation_output(value: ObservationStepResult | ObservationOutput | Mapping[str, Any]) -> ObservationOutput:
    if isinstance(value, ObservationStepResult):
        return value.output
    if isinstance(value, ObservationOutput):
        return value
    if isinstance(value, Mapping):
        payload = dict(value)
        return ObservationOutput(
            raw_stimulus=payload.get("raw_stimulus"),
            representation=payload.get("representation"),
            context_state=payload.get("context_state"),
            generalized_state=payload.get("generalized_state"),
            features=list(payload.get("features", []) or []),
            feature_names=list(payload.get("feature_names", []) or []),
            metadata=dict(payload.get("metadata", {}) or {}),
        )
    raise TypeError("observation must be ObservationStepResult, ObservationOutput, or object payload.")


def _coerce_prediction_output(value: PredictionOutput | Mapping[str, Any] | float | int) -> PredictionOutput:
    if isinstance(value, PredictionOutput):
        return value
    if isinstance(value, Mapping):
        payload = dict(value)
        if payload.get("action_values"):
            return PredictionOutput.from_action_values(
                action_values=dict(payload.get("action_values", {}) or {}),
                metadata=dict(payload.get("metadata", {}) or {}),
            )
        return PredictionOutput.from_state_value(
            float(payload.get("state_value", 0.0)),
            metadata=dict(payload.get("metadata", {}) or {}),
        )
    if isinstance(value, (int, float)):
        return PredictionOutput.from_state_value(float(value))
    raise TypeError("prediction must be PredictionOutput, object payload, or numeric state value.")


def _features_to_mapping(*, features: Sequence[float], feature_names: Sequence[str]) -> dict[str, float]:
    names = [str(name) for name in feature_names]
    values = [float(v) for v in features]
    if len(names) != len(values):
        raise ValueError("observation feature_names length must match features length.")
    return dict(zip(names, values))


@dataclass(frozen=True)
class AgentStepResult:
    """Typed compositional agent step artifact."""

    observation_output: ObservationOutput
    prediction_output: PredictionOutput
    policy_output: PolicyOutput
    action: Action
    learner_step_result: LearnerStepResult | None = None
    transition: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class CompositionalAgent:
    """
    Thin runtime orchestrator with explicit causal split:
    pre-outcome: observe -> predict -> act
    post-outcome: learn -> advance_internal_time
    """

    observation_adapter: RuntimeObservationAdapter = field(default_factory=build_runtime_observation_adapter)
    learner_adapter: RuntimeLearnerAdapter = field(default_factory=build_runtime_learner_adapter)
    policy_adapter: RuntimePolicyAdapter = field(default_factory=build_runtime_policy_adapter)
    internal_time_s: float = 0.0

    _last_task_input: TaskInput | None = field(default=None, init=False, repr=False)
    _last_observation_output: ObservationOutput | None = field(default=None, init=False, repr=False)
    _last_prediction_output: PredictionOutput | None = field(default=None, init=False, repr=False)
    _last_policy_output: PolicyOutput | None = field(default=None, init=False, repr=False)

    def observe(self, task_input: TaskInput | Mapping[str, Any]) -> ObservationStepResult:
        ti = _coerce_task_input(task_input)
        observation_step = self.observation_adapter.step(
            stimulus=ti.stimuli,
            context_state=ti.context,
            metadata={
                **dict(ti.metadata),
                "agent_stage": "observe",
                "agent_internal_time_s": float(self.internal_time_s),
                "task_t": ti.t,
                "task_phase": ti.phase,
            },
        )
        self._last_task_input = ti
        self._last_observation_output = observation_step.output
        return observation_step

    def predict(
        self,
        observation: ObservationStepResult | ObservationOutput | Mapping[str, Any] | None = None,
    ) -> PredictionOutput:
        current_observation = (
            self._last_observation_output
            if observation is None
            else _coerce_observation_output(observation)
        )
        if current_observation is None:
            raise ValueError("No observation available. Call observe(...) first or provide observation explicitly.")
        feature_map = _features_to_mapping(
            features=current_observation.features,
            feature_names=current_observation.feature_names,
        )
        raw_prediction = self.learner_adapter.bundle.predictor(
            features=feature_map,
            state=self.learner_adapter.bundle.state,
        )
        prediction = _coerce_prediction_output(raw_prediction)
        self._last_prediction_output = prediction
        return prediction

    def act(
        self,
        prediction: PredictionOutput | Mapping[str, Any] | float | int | None = None,
    ) -> PolicyOutput:
        if self._last_observation_output is None:
            raise ValueError("No observation available. Call observe(...) first.")
        if self._last_task_input is None:
            raise ValueError("No task_input available. Call observe(...) first.")
        resolved_prediction = (
            self._last_prediction_output if prediction is None else _coerce_prediction_output(prediction)
        )
        if resolved_prediction is None:
            raise ValueError("No prediction available. Call predict(...) first or provide prediction explicitly.")
        policy_output = self.policy_adapter.step(
            task_input=self._last_task_input,
            observation_output=self._last_observation_output,
            prediction=resolved_prediction,
            available_actions=self._last_task_input.available_actions,
            metadata={
                "agent_stage": "act",
                "agent_internal_time_s": float(self.internal_time_s),
            },
        )
        self._last_policy_output = policy_output
        return policy_output

    def pre_outcome_step(self, task_input: TaskInput | Mapping[str, Any]) -> AgentStepResult:
        observation = self.observe(task_input)
        prediction = self.predict(observation)
        policy = self.act(prediction)
        action = Action(value=policy.action, metadata=dict(policy.metadata))
        return AgentStepResult(
            observation_output=observation.output,
            prediction_output=prediction,
            policy_output=policy,
            action=action,
            learner_step_result=None,
            transition={},
            metadata={
                "pipeline_order": ["observe", "predict", "act"],
                "agent_internal_time_s": float(self.internal_time_s),
            },
        )

    def learn(
        self,
        observation: ObservationStepResult | ObservationOutput | Mapping[str, Any],
        prediction: PredictionOutput | Mapping[str, Any] | float | int,
        action: Action | Any,
        outcome: Outcome | Mapping[str, Any],
    ) -> LearnerStepResult:
        observation_output = _coerce_observation_output(observation)
        prediction_output = _coerce_prediction_output(prediction)
        action_boundary = _coerce_action(action)
        outcome_boundary = _coerce_outcome(outcome)

        next_observation_output: ObservationOutput | None = None
        if outcome_boundary.next_stimuli:
            next_step = self.observation_adapter.step(
                stimulus=outcome_boundary.next_stimuli,
                context_state=self._last_task_input.context if self._last_task_input is not None else None,
                metadata={
                    **dict(outcome_boundary.metadata),
                    "agent_stage": "observe_next",
                    "agent_internal_time_s": float(self.internal_time_s),
                },
            )
            next_observation_output = next_step.output

        learner_step = self.learner_adapter.step(
            observation_features=observation_output.features,
            observation_feature_names=observation_output.feature_names,
            next_observation_features=None if next_observation_output is None else next_observation_output.features,
            next_observation_feature_names=None
            if next_observation_output is None
            else next_observation_output.feature_names,
            reward=float(outcome_boundary.reward),
            done=bool(outcome_boundary.terminated or outcome_boundary.truncated),
        )

        self._last_prediction_output = prediction_output
        self._last_policy_output = PolicyOutput(
            action=action_boundary.value,
            metadata=dict(action_boundary.metadata),
        )
        return learner_step

    def advance_internal_time(self, dt: float | int) -> float:
        delta = float(dt)
        self.internal_time_s = float(self.internal_time_s) + delta
        return self.internal_time_s
