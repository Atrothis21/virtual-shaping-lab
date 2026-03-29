"""Test-mode rollout harness for V3 environment stepping."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

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


class CompiledProgramTestEnvironment(IEnvironment):
    """Deterministic environment adapter over compiled EnvironmentProgram."""

    def __init__(
        self,
        program: EnvironmentProgram,
        *,
        learner_adapter: RuntimeLearnerAdapter | None = None,
        observation_adapter: RuntimeObservationAdapter | None = None,
    ):
        self._program = program
        self._timeline: list[tuple[str, str, str, int, dict[str, Any], dict[str, Any], float]] = []
        self._cursor = 0
        self._done = False
        self._learner_adapter = learner_adapter or build_runtime_learner_adapter()
        self._observation_adapter = observation_adapter or build_runtime_observation_adapter()
        self._build_timeline()

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
        next_trial_meta = None
        if not self._done:
            next_stimulus = dict(self._timeline[self._cursor][4])
            next_trial_meta = dict(self._timeline[self._cursor][5])
        termination = EnvironmentTermination(
            done=self._done,
            reason="terminal" if self._done else "running",
            metadata={"cursor": self._cursor},
        )
        family = str(trial_meta.get("family", ""))
        is_operant = _is_operant_semantics(protocol, family)
        observation_step = self._observation_adapter.step(
            stimulus=stimulus,
            context_state=trial_meta.get("context_state", trial_meta.get("context")),
            metadata={
                "segment_key": segment_key,
                "protocol": protocol,
                "trial_type": trial_type,
                "step_index": step_index,
            },
        )
        next_observation_step = None
        if next_stimulus is not None:
            next_observation_step = self._observation_adapter.step(
                stimulus=next_stimulus,
                context_state=None
                if next_trial_meta is None
                else next_trial_meta.get("context_state", next_trial_meta.get("context")),
                metadata={
                    "segment_key": segment_key,
                    "protocol": protocol,
                    "trial_type": trial_type,
                    "step_index": step_index + 1,
                },
            )
        learner_step = self._learner_adapter.step(
            observation_features=observation_step.output.features,
            observation_feature_names=observation_step.output.feature_names,
            next_observation_features=None if next_observation_step is None else next_observation_step.output.features,
            next_observation_feature_names=None
            if next_observation_step is None
            else next_observation_step.output.feature_names,
            reward=float(reward),
            done=self._done,
        )
        trial_state = TrialState.with_action_semantics(
            s={"segment_key": segment_key, "step_index": step_index, "trial_index": trial_index},
            x=dict(stimulus),
            z={"protocol": protocol},
            w=dict(trial_meta),
            y=float(reward),
            is_operant=is_operant,
            action=action,
            available_actions=[action] if action is not None else [],
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
            action=action,
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
                    "output": observation_step.output.to_dict(),
                    "measurements": dict(observation_step.measurements),
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
