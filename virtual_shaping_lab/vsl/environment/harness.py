"""Test-mode rollout harness for V3 environment stepping."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from virtual_shaping_lab.vsl._migration import warn_deprecated_import
from virtual_shaping_lab.vsl.environment.contracts import (
    EnvironmentReset,
    EnvironmentStep,
    EnvironmentTermination,
    IEnvironment,
)
from virtual_shaping_lab.vsl.environment.trial_state import TrialState
from virtual_shaping_lab.vsl.program.types import EnvironmentProgram

warn_deprecated_import(
    "virtual_shaping_lab.vsl.environment.harness",
    "virtual_shaping_lab.vsl.rollout.harness",
    removal_release="V3.10.0",
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

    def __init__(self, program: EnvironmentProgram):
        self._program = program
        self._timeline: list[tuple[str, str, str, int, dict[str, Any], dict[str, Any], float]] = []
        self._cursor = 0
        self._done = False
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
        termination = EnvironmentTermination(
            done=self._done,
            reason="terminal" if self._done else "running",
            metadata={"cursor": self._cursor},
        )
        family = str(trial_meta.get("family", ""))
        is_operant = _is_operant_semantics(protocol, family)
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
            prediction=None,
            error=None,
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
            metadata={"trial": trial_meta},
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
