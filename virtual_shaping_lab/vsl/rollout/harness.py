"""Test-mode rollout harness for V3 environment stepping."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import Any

from virtual_shaping_lab.vsl.agent.composite import CompositionalAgent
from virtual_shaping_lab.vsl.contracts import Outcome, TaskInput
from virtual_shaping_lab.vsl.environment.contracts import (
    EnvironmentReset,
    EnvironmentStep,
    EnvironmentTermination,
    IEnvironment,
)
from virtual_shaping_lab.vsl.rollout.trial_state import TrialState
from virtual_shaping_lab.vsl.program.types import EnvironmentProgram
from virtual_shaping_lab.vsl.runtime.learner_adapter import (
    RuntimeLearnerAdapter,
    build_runtime_learner_adapter,
)
from virtual_shaping_lab.vsl.runtime.observation_adapter import (
    RuntimeObservationAdapter,
    build_runtime_observation_adapter,
)
from virtual_shaping_lab.vsl.runtime.policy_adapter import (
    RuntimePolicyAdapter,
    build_runtime_policy_adapter,
)


def _reward_from_trial_params(params: dict[str, Any]) -> float:
    for key in ("outcome", "reward", "reward_value"):
        if key in params:
            try:
                return float(params.get(key, 0.0) or 0.0)
            except (TypeError, ValueError):
                return 0.0
    return 0.0


_OPERANT_PROTOCOLS = {
    "operant_conditioning",
    "matching_law",
    "shaping",
    "resurgence",
    "superextinction",
    "spontaneous_recovery",
    "operant_phase_template",
}


def _is_operant_semantics(protocol: str, family: str) -> bool:
    if family in {"template_operant", "protocol_recipe_operant"}:
        return True
    return protocol in _OPERANT_PROTOCOLS


def _extract_available_actions(trial_meta: dict[str, Any]) -> tuple[Any, ...]:
    for key in ("available_actions", "actions", "action_set"):
        raw = trial_meta.get(key)
        if isinstance(raw, (list, tuple)):
            return tuple(raw)
        if raw is not None:
            return (raw,)
    return ()


class CompiledProgramTestEnvironment(IEnvironment):
    """Deterministic environment adapter over compiled EnvironmentProgram."""

    def __init__(
        self,
        program: EnvironmentProgram,
        *,
        learner_adapter: RuntimeLearnerAdapter | None = None,
        observation_adapter: RuntimeObservationAdapter | None = None,
        policy_adapter: RuntimePolicyAdapter | None = None,
    ):
        self._program = program
        self._timeline: list[tuple[str, str, str, int, dict[str, Any], dict[str, Any], float]] = []
        self._cursor = 0
        self._done = False
        self._learner_adapter = learner_adapter or build_runtime_learner_adapter()
        self._observation_adapter = observation_adapter or build_runtime_observation_adapter()
        self._policy_adapter = policy_adapter or build_runtime_policy_adapter()
        self._initial_learner_state: dict[str, Any] | None = None
        self._initial_attention_state: dict[str, Any] | None = None
        self._initial_eligibility_state: dict[str, Any] | None = None
        self._snapshot_initial_runtime_state()
        self._agent = CompositionalAgent(
            observation_adapter=self._observation_adapter,
            learner_adapter=self._learner_adapter,
            policy_adapter=self._policy_adapter,
        )
        self._build_timeline()

    def _snapshot_initial_runtime_state(self) -> None:
        bundle = getattr(self._learner_adapter, "bundle", None)
        if bundle is None:
            return
        self._initial_learner_state = deepcopy(getattr(bundle, "state", {}))
        self._initial_attention_state = deepcopy(getattr(bundle, "attention_state", None))
        self._initial_eligibility_state = deepcopy(getattr(bundle, "eligibility_state", None))

    def _restore_runtime_state_for_reset(self) -> None:
        bundle = getattr(self._learner_adapter, "bundle", None)
        if bundle is not None:
            if self._initial_learner_state is not None:
                bundle.state = deepcopy(self._initial_learner_state)
            if hasattr(bundle, "attention_state"):
                bundle.attention_state = deepcopy(self._initial_attention_state)
            if hasattr(bundle, "eligibility_state"):
                bundle.eligibility_state = deepcopy(self._initial_eligibility_state)
        # Always recreate the orchestrator to clear per-step caches and internal time.
        self._agent = CompositionalAgent(
            observation_adapter=self._observation_adapter,
            learner_adapter=self._learner_adapter,
            policy_adapter=self._policy_adapter,
        )

    def _build_timeline(self) -> None:
        timeline: list[tuple[str, str, str, int, dict[str, Any], dict[str, Any], float]] = []
        for segment in self._program.segments:
            for trial in segment.trials:
                reward = _reward_from_trial_params(trial.params)
                for idx in range(int(trial.n_trials)):
                    timeline.append(
                        (
                            segment.key,
                            segment.protocol,
                            trial.trial_type,
                            idx,
                            dict(trial.stimuli),
                            dict(trial.metadata),
                            reward,
                        )
                    )
        self._timeline = timeline
        self._done = len(self._timeline) == 0

    @property
    def done(self) -> bool:
        return self._done

    def reset(self, *, seed: int | None = None) -> EnvironmentReset:
        # Deterministic test-mode environment does not consume randomness yet.
        normalized_seed = int(seed) if seed is not None else None
        self._cursor = 0
        self._done = len(self._timeline) == 0
        self._restore_runtime_state_for_reset()
        return EnvironmentReset(
            seed=normalized_seed,
            done=self._done,
            metadata={"source": "compiled_program_test_environment"},
        )

    def step(self, action: Any = None) -> EnvironmentStep:
        if self._done:
            raise StopIteration("Environment is already terminal.")
        segment_key, protocol, trial_type, trial_index, stimulus, trial_meta, reward = self._timeline[self._cursor]
        step_index = self._cursor
        self._cursor += 1
        self._done = self._cursor >= len(self._timeline)
        next_stimulus = None
        if not self._done:
            next_stimulus = dict(self._timeline[self._cursor][4])
        termination = EnvironmentTermination(
            done=self._done,
            reason="terminal" if self._done else "running",
            metadata={"cursor": self._cursor},
        )
        family = str(trial_meta.get("family", ""))
        is_operant = _is_operant_semantics(protocol, family)
        declared_available_actions = _extract_available_actions(trial_meta)

        # Single-path compositional execution:
        # pre-outcome (observe -> predict -> act), then post-outcome (learn -> advance).
        task_input = TaskInput(
            stimuli=dict(stimulus),
            context=trial_meta.get("context_state", trial_meta.get("context")),
            t=step_index,
            phase=protocol,
            available_actions=declared_available_actions,
            metadata={
                "segment_key": segment_key,
                "protocol": protocol,
                "trial_type": trial_type,
                "step_index": step_index,
            },
        )
        pre = self._agent.pre_outcome_step(task_input)
        chosen_action = action if action is not None else pre.action.value
        learner_step = self._agent.learn(
            observation=pre.observation_output,
            prediction=pre.prediction_output,
            action=chosen_action,
            outcome=Outcome(
                reward=float(reward),
                next_stimuli={} if next_stimulus is None else dict(next_stimulus),
                terminated=bool(self._done),
                truncated=False,
                metadata={
                    "segment_key": segment_key,
                    "protocol": protocol,
                    "trial_type": trial_type,
                    "step_index": step_index,
                },
            ),
        )
        self._agent.advance_internal_time(1.0)
        policy_output = pre.policy_output
        observation_step = pre
        available_for_state = (
            list(policy_output.available_actions)
            if policy_output.available_actions
            else ([chosen_action] if chosen_action is not None else [])
        )
        trial_state = TrialState.with_action_semantics(
            s={"segment_key": segment_key, "step_index": step_index, "trial_index": trial_index},
            x=dict(stimulus),
            z={"protocol": protocol},
            w=dict(trial_meta),
            y=float(reward),
            is_operant=is_operant,
            action=chosen_action,
            available_actions=available_for_state,
            persistent={"termination": termination.to_dict()},
            attention_state=learner_step.attention_state,
            prediction=learner_step.prediction,
            error=learner_step.error,
        )
        return EnvironmentStep(
            step_index=step_index,
            segment_key=segment_key,
            protocol=protocol,
            trial_type=trial_type,
            trial_index=trial_index,
            action=chosen_action,
            stimulus=stimulus,
            reward=reward,
            done=self._done,
            trial_state=trial_state,
            termination=termination,
            metadata={
                "trial": trial_meta,
                "learner": {
                    "prediction": learner_step.prediction,
                    "next_prediction": learner_step.next_prediction,
                    "error": learner_step.error,
                    "update_features": learner_step.update_features,
                    "input_features": dict(learner_step.features),
                    "attention_state": learner_step.attention_state,
                    "eligibility_state": learner_step.eligibility_state,
                },
                "observation": {
                    "output": observation_step.observation_output.to_dict(),
                    "measurements": {
                        "n_features": len(observation_step.observation_output.features),
                        "feature_names": list(observation_step.observation_output.feature_names),
                        "pipeline_order": list(
                            observation_step.observation_output.metadata.get("pipeline_order", [])
                        ),
                    },
                },
                "policy": {
                    "action": policy_output.action,
                    "available_actions": list(policy_output.available_actions),
                    "action_scores": dict(policy_output.action_scores),
                    "action_probabilities": dict(policy_output.action_probabilities),
                    "metadata": {
                        **dict(policy_output.metadata),
                        "action_source": "runtime_policy_adapter",
                    },
                },
            },
        )


@dataclass
class RolloutHarness:
    """Rollout harness that executes an IEnvironment in deterministic test mode."""

    max_steps: int | None = None

    def run(self, environment: IEnvironment, *, seed: int | None = None, action: Any = None) -> list[dict[str, Any]]:
        environment.reset(seed=seed)
        emitted: list[dict[str, Any]] = []
        steps = 0
        while not environment.done:
            step = environment.step(action=action)
            emitted.append(step.to_dict())
            steps += 1
            if self.max_steps is not None and steps >= self.max_steps:
                break
        return emitted
