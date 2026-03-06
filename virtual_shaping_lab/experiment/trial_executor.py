"""Tick-level trial execution helper for intra-trial runtime updates."""

from __future__ import annotations

from dataclasses import replace
from typing import Any
from collections.abc import Mapping

from virtual_shaping_lab.domain.types import Observation, Transition
from virtual_shaping_lab.experiment.debug_policy import (
    DEBUG_MODE_BOTH,
    DEBUG_MODE_TICK,
    DEBUG_MODE_TRIAL,
    DebugTelemetryPolicy,
    resolve_debug_policy,
)
from virtual_shaping_lab.experiment.domain.types import ExperimentContext, StepResult, TrialSchedule
from virtual_shaping_lab.experiment.world.schedules import ScheduleTickInput


_STIMULUS_EVENT_TYPES = {"stimulus", "cs", "cue"}
_REINFORCEMENT_EVENT_TYPES = {"reward", "reinforcement", "us"}


class TrialExecutor:
    """Execute one trial schedule at tick resolution."""

    def __init__(
        self,
        *,
        update_mode: str = "trial",
        record_mode: str = "trial",
        debug: bool = False,
        debug_policy: Mapping[str, Any] | DebugTelemetryPolicy | None = None,
    ):
        if update_mode not in {"trial", "tick"}:
            raise ValueError("update_mode must be one of {'trial', 'tick'}.")
        if record_mode not in {"trial", "tick"}:
            raise ValueError("record_mode must be one of {'trial', 'tick'}.")
        self.update_mode = update_mode
        self.record_mode = record_mode
        self.debug = bool(debug)
        if isinstance(debug_policy, DebugTelemetryPolicy):
            self.debug_policy = debug_policy
        else:
            self.debug_policy = resolve_debug_policy(
                debug_policy if isinstance(debug_policy, Mapping) else None,
                fallback_debug_flag=self.debug,
            )

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

    @staticmethod
    def _safe_value(agent: Any, state: Any, action: Any) -> float | None:
        if agent is None or not hasattr(agent, "value"):
            return None
        try:
            value = agent.value(state, action=action)
        except TypeError:
            try:
                value = agent.value(state, action)
            except TypeError:
                value = agent.value(state)
        except Exception:
            return None
        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _mapping_to_float_dict(value: Any) -> dict[str, float] | None:
        if not isinstance(value, Mapping):
            return None
        out: dict[str, float] = {}
        for key, item in value.items():
            try:
                out[str(key)] = float(item)
            except (TypeError, ValueError):
                continue
        return out

    def _build_debug_payload(
        self,
        *,
        agent: Any,
        state: Any,
        action: Any,
        reward: float,
        active_stimuli: list[Any],
    ) -> dict[str, Any]:
        value = self._safe_value(agent, state, action)
        prediction_error = (reward - value) if value is not None else None

        learner = getattr(agent, "learner", None) if agent is not None else None
        attention_effective = self._mapping_to_float_dict(getattr(learner, "attention_map", None))
        if attention_effective is None:
            attention_effective = self._mapping_to_float_dict(getattr(learner, "attention", None))

        representation = getattr(agent, "representation", None) if agent is not None else None
        salience_effective = self._mapping_to_float_dict(getattr(representation, "salience", None))

        return {
            "value": value,
            "prediction_error": prediction_error,
            "active_features": [str(s) for s in active_stimuli],
            "attention_effective": attention_effective if attention_effective is not None else {},
            "salience_effective": salience_effective if salience_effective is not None else {},
        }

    def _policy_allows_tick_debug(self, tick: int) -> bool:
        if not self.debug_policy.enabled:
            return False
        if self.debug_policy.mode not in {DEBUG_MODE_TICK, DEBUG_MODE_BOTH}:
            return False
        every_n = self.debug_policy.sample_every_n_ticks
        if every_n is not None and (tick % every_n) != 0:
            return False
        return True

    def _policy_allows_trial_debug(self) -> bool:
        if not self.debug_policy.enabled:
            return False
        return self.debug_policy.mode in {DEBUG_MODE_TRIAL, DEBUG_MODE_BOTH}

    def _apply_debug_policy(self, debug_payload: dict[str, Any]) -> dict[str, Any]:
        out = dict(debug_payload)
        cap = self.debug_policy.max_active_features
        if cap is not None and isinstance(out.get("active_features"), list):
            out["active_features"] = out["active_features"][:cap]
        return out

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
        schedule_runtime = None
        if isinstance(getattr(schedule, "metadata", None), dict):
            schedule_runtime = schedule.metadata.get("schedule_runtime")
        if schedule_runtime is not None and hasattr(schedule_runtime, "reset"):
            schedule_runtime.reset(ctx.rng)
        if hooks is not None and hasattr(hooks, "on_trial_start"):
            hooks.on_trial_start(unit=unit, ctx=ctx, trial_id=trial_id, step=step)
        last_debug_payload: dict[str, Any] | None = None

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

            event_reward = float(
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

            runtime_reward = 0.0
            runtime_event_type = None
            runtime_meta: dict[str, Any] = {}
            if schedule_runtime is not None and hasattr(schedule_runtime, "step"):
                runtime_out = schedule_runtime.step(
                    ScheduleTickInput(
                        t_s=t_s,
                        dt_s=dt_tick,
                        action=action,
                        tick=tick,
                        trial_id=trial_id,
                    )
                )
                runtime_reward = float(getattr(runtime_out, "reward", 0.0) or 0.0)
                runtime_event_type = getattr(runtime_out, "event_type", None)
                runtime_meta = dict(getattr(runtime_out, "metadata", {}) or {})
            reward = event_reward + runtime_reward
            if self.debug_policy.enabled:
                last_debug_payload = self._build_debug_payload(
                    agent=agent,
                    state=state,
                    action=action,
                    reward=reward,
                    active_stimuli=active_stimuli,
                )

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
                "schedule_runtime_event_type": runtime_event_type,
                "schedule_runtime": runtime_meta,
            }

            if self.record_mode == "tick":
                tick_record = {
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
                if (
                    last_debug_payload is not None
                    and self._policy_allows_tick_debug(tick)
                ):
                    tick_record["debug"] = self._apply_debug_policy(last_debug_payload)
                trial_records.append(tick_record)

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

        if (
            self.record_mode != "tick"
            and last_debug_payload is not None
            and self._policy_allows_trial_debug()
        ):
            base_record["debug"] = self._apply_debug_policy(last_debug_payload)
        emitted = trial_records if self.record_mode == "tick" else [base_record]

        if hooks is not None and hasattr(hooks, "on_trial_end"):
            hooks.on_trial_end(unit=unit, ctx=ctx, trial_id=trial_id, records=emitted)

        return emitted
