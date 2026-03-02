"""Runnable template phase composed from mechanics strategies."""

from __future__ import annotations

from typing import Any

import numpy as np

from experiment.domain.types import (
    ExperimentContext,
    OperantContingencySpec,
    PavlovianContingencySpec,
    PhaseSpec,
    StepResult,
)
from experiment.phases.templates.interfaces import (
    ILearningGate,
    IRecordBuilder,
    ITrialSampler,
    ITrialScheduleBuilder,
)
from virtual_shaping_lab.domain.types import Observation, Transition


class PhaseTemplate:
    """Thin runnable orchestrator for spec-driven phase execution."""

    def __init__(
        self,
        *,
        agent: Any,
        spec: PhaseSpec,
        trial_sampler: ITrialSampler,
        trial_schedule_builder: ITrialScheduleBuilder,
        learning_gate: ILearningGate,
        record_builder: IRecordBuilder,
    ):
        self.agent = agent
        self.spec = spec
        self.trial_sampler = trial_sampler
        self.trial_schedule_builder = trial_schedule_builder
        self.learning_gate = learning_gate
        self.record_builder = record_builder
        self.trial_index = 0
        self.records: list[dict[str, Any]] = []
        self._rng: np.random.Generator | None = None
        self.name = spec.name
        self.context = spec.context_id or "A"
        self.n_trials = int(spec.n_trials)

    def reset(self, ctx: ExperimentContext) -> None:
        self.trial_index = 0
        self.records = []
        self._rng = ctx.rng
        self.trial_sampler.reset()

    def has_next_trial(self) -> bool:
        return self.trial_index < self.n_trials

    def _resolve_reward(self, contingency: Any) -> float:
        if isinstance(contingency, PavlovianContingencySpec):
            return float(contingency.us_magnitude)
        if isinstance(contingency, OperantContingencySpec):
            # Operant reward typically comes from schedule/task runtime.
            # Keep base trial reward neutral unless explicitly modeled elsewhere.
            return 0.0
        return 0.0

    def iter_steps(self, ctx: ExperimentContext):
        if self._rng is None:
            self.reset(ctx)

        while self.has_next_trial():
            trial_type = self.trial_sampler.select_trial_type(
                spec=self.spec,
                trial_index=self.trial_index,
                rng=self._rng if self._rng is not None else np.random.default_rng(),
            )
            schedule = self.trial_schedule_builder.build_schedule(
                spec=self.spec,
                trial_type=trial_type,
                trial_index=self.trial_index,
            )

            observation = Observation(
                stimuli=list(trial_type.stimuli),
                context=self.context,
                trial_step=self.trial_index,
                trial_id=self.trial_index,
            )
            reward = self._resolve_reward(self.spec.contingency)
            action = None
            state = None
            available_actions: list[Any] = []
            if isinstance(self.spec.contingency, OperantContingencySpec):
                available_actions = list(self.spec.contingency.action_labels)

            if self.agent is not None and hasattr(self.agent, "observe"):
                state = self.agent.observe(observation)
                if available_actions and hasattr(self.agent, "act"):
                    action = self.agent.act(state, actions=available_actions, rng=self._rng)

            learning_enabled = self.learning_gate.allows_learning(
                spec=self.spec,
                trial_index=self.trial_index,
            )
            if (
                learning_enabled
                and state is not None
                and self.agent is not None
                and hasattr(self.agent, "learn")
            ):
                self.agent.learn(
                    Transition(
                        s=state,
                        a=action,
                        r=reward,
                        s_next=None,
                        done=False,
                        trial_step=self.trial_index,
                        trial_id=self.trial_index,
                    )
                )

            record = self.record_builder.build_record(
                spec=self.spec,
                trial_type=trial_type,
                trial_index=self.trial_index,
                reward=reward,
                action=action,
                context=self.context,
            )
            self.records.append(record)

            metadata = {"record": record}
            if schedule is not None:
                metadata["trial_schedule"] = schedule

            done = self.trial_index >= self.n_trials - 1
            self.trial_index += 1
            yield StepResult(
                observation=observation,
                available_actions=available_actions,
                reward=reward,
                learning_enabled=learning_enabled,
                done=done,
                metadata=metadata,
            )
