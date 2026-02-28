"""Tick-level trial execution helper for intra-trial runtime updates."""

from __future__ import annotations

from dataclasses import replace
from typing import Any

from virtual_shaping_lab.domain.types import Observation, Transition
from virtual_shaping_lab.experiment.domain.types import ExperimentContext, StepResult, TrialSchedule


_STIMULUS_EVENT_TYPES = {"stimulus", "cs", "cue"}
_REINFORCEMENT_EVENT_TYPES = {"reward", "reinforcement", "us"}


class TrialExecutor:
    """Execute one trial schedule at tick resolution."""

    def __init__(self, *, update_mode: str = "trial", record_mode: str = "trial"):
        if update_mode not in {"trial", "tick"}:
            raise ValueError("update_mode must be one of {'trial', 'tick'}.")
        if record_mode not in {"trial", "tick"}:
            raise ValueError("record_mode must be one of {'trial', 'tick'}.")
        self.update_mode = update_mode
        self.record_mode = record_mode

    @staticmethod
    def _event_active(start_s: float, end_s: float, t_s: float, t_next_s: float) -> bool:
        return (start_s < t_next_s) and (end_s > t_s)

    def _iter_tick_times(self, duration_s: float, dt_s: float, allow_partial_last_step: bool):
        t_s = 0.0
        tick = 0
        while t_s < duration_s:
            t_next_s = t_s + dt_s
            if t_next_s > duration_s and not allow_partial_last_step:
                break
            dt_tick = min(dt_s, duration_s - t_s)
            yield tick, t_s, dt_tick, t_next_s
            tick += 1
            t_s = t_next_s

    def execute(
        self,
        *,
        ctx: ExperimentContext,
        step: StepResult,
        schedule: TrialSchedule,
        base_record: dict[str, Any],
        trial_id: Any,
        hooks: Any = None,
        unit: Any = None,
    ) -> list[dict[str, Any]]:
        spec = schedule.time
        trial_records: list[dict[str, Any]] = []
        agent = ctx.agent
        if hooks is not None and hasattr(hooks, "on_trial_start"):
            hooks.on_trial_start(unit=unit, ctx=ctx, trial_id=trial_id, step=step)

        for tick, t_s, dt_tick, t_next_s in self._iter_tick_times(
            spec.duration_s, spec.dt_s, spec.allow_partial_last_step
        ):
            active_events = [
                e for e in spec.events if self._event_active(e.start_s, e.end_s, t_s, t_next_s)
            ]
            active_windows = [
                w for w in spec.response_windows if self._event_active(w.start_s, w.end_s, t_s, t_next_s)
            ]

            active_stimuli = list(schedule.base_stimuli)
            for event in active_events:
                if event.event_type in _STIMULUS_EVENT_TYPES:
                    stim_label = event.metadata.get("stimulus", event.metadata.get("label", event.event_type))
                    active_stimuli.append(stim_label)

            reward = float(
                sum(e.magnitude for e in active_events if e.event_type in _REINFORCEMENT_EVENT_TYPES)
            )
            actions = list(schedule.available_actions)
            if spec.response_windows and not active_windows:
                actions = []

            observation = replace(
                step.observation,
                stimuli=active_stimuli,
                t_s=t_s,
                dt_s=dt_tick,
                trial_step=tick,
                trial_id=trial_id,
            )

            action = None
            state = None
            if agent is not None and hasattr(agent, "observe"):
                state = agent.observe(observation)
                if actions and hasattr(agent, "act"):
                    action = agent.act(state, actions=actions, rng=ctx.rng)

            if (
                self.update_mode == "tick"
                and step.learning_enabled
                and state is not None
                and agent is not None
                and hasattr(agent, "learn")
            ):
                agent.learn(
                    Transition(
                        s=state,
                        a=action,
                        r=reward,
                        s_next=None,
                        done=False,
                        t_s=t_s,
                        dt_s=dt_tick,
                        trial_step=tick,
                        trial_id=trial_id,
                    )
                )

            tick_meta = {
                "active_event_types": [e.event_type for e in active_events],
                "active_windows": [w.label for w in active_windows],
            }

            if self.record_mode == "tick":
                trial_records.append(
                    {
                        "phase": base_record.get("phase", "runnable_unit"),
                        "trial": base_record.get("trial", trial_id),
                        "tick": tick,
                        "t_s": t_s,
                        "dt_s": dt_tick,
                        "stimuli": active_stimuli,
                        "action": action,
                        "reward": reward,
                        "context": observation.context,
                        "metadata": tick_meta,
                    }
                )

            if hooks is not None and hasattr(hooks, "on_tick"):
                hooks.on_tick(
                    unit=unit,
                    ctx=ctx,
                    trial_id=trial_id,
                    tick=tick,
                    observation=observation,
                    action=action,
                    reward=reward,
                    metadata=tick_meta,
                )

        ctx.clock_s += spec.duration_s + spec.iti_s

        emitted = trial_records if self.record_mode == "tick" else [base_record]

        if hooks is not None and hasattr(hooks, "on_trial_end"):
            hooks.on_trial_end(unit=unit, ctx=ctx, trial_id=trial_id, records=emitted)

        return emitted
