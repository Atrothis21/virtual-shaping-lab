# experiment/runner.py

from typing import List, Dict, Any, Optional, Protocol, runtime_checkable

import numpy as np

from experiment.domain.types import ExperimentContext
from experiment.hooks import RunnerHooks
from experiment.parameters import validate_composed_parameter_ownership
from experiment.sinks import InMemorySink
from experiment.trial_executor import TrialExecutor
from virtual_shaping_lab.domain.types import Observation
from virtual_shaping_lab.experiment.domain.types import TrialSchedule, TrialTimeSpec
from virtual_shaping_lab.experiment.runtime_records import finalize_record
from virtual_shaping_lab.vsl.environment import IEnvironment, TrialState


@runtime_checkable
class RunnableUnitLike(Protocol):
    def reset(self, ctx: ExperimentContext) -> None: ...
    def iter_steps(self, ctx: ExperimentContext): ...


class Runner:
    """
    Execute runtime units and collect trial records.

    The runner is intentionally thin:
    - It does NOT control trial logic
    - It does NOT inspect internals beyond run/step
    - It simply delegates execution

    Deterministic replay contract:
    - identical runtime units + canonical plan inputs + seed must reproduce
      identical context RNG streams and emitted record order
    - stochastic policy and schedule paths must consume the shared runtime RNG
      built here rather than creating independent generators
    """

    def __init__(
        self,
        runtime_units,
        *,
        seed: Optional[int] = None,
        context: Optional[ExperimentContext] = None,
        settings: Optional[dict[str, Any]] = None,
        sink: Optional[Any] = None,
        hooks: Optional[RunnerHooks] = None,
    ):
        self.runtime_units = runtime_units
        self.seed = seed
        self.context = context
        self.settings = settings or {}
        composed = self.settings.get("composed_parameters")
        if composed:
            validate_composed_parameter_ownership(composed)
        self.sink = sink if sink is not None else InMemorySink()
        self._owns_sink = sink is None
        self.hooks = hooks or RunnerHooks()
        runtime_settings = {}
        if isinstance(composed, dict):
            runtime = composed.get("runtime")
            if isinstance(runtime, dict):
                runtime_settings = runtime
        self.update_mode = self.settings.get("update_mode", runtime_settings.get("update_mode", "trial"))
        self.record_mode = self.settings.get("record_mode", runtime_settings.get("record_mode", "trial"))
        self.debug_mode = bool(self.settings.get("debug", runtime_settings.get("debug", False)))
        debug_policy_settings = dict(runtime_settings)
        for key in (
            "debug",
            "debug_mode",
            "debug_max_active_features",
            "debug_sample_every_n_ticks",
        ):
            if key in self.settings:
                debug_policy_settings[key] = self.settings[key]
        self._trial_executor = TrialExecutor(
            update_mode=self.update_mode,
            record_mode=self.record_mode,
            debug=self.debug_mode,
            debug_policy=debug_policy_settings,
        )

    def _emit_record(self, record: Dict[str, Any]) -> None:
        self.sink.emit(record)

    def _build_context(self, unit: Any) -> ExperimentContext:
        if self.context is not None:
            return self.context

        agent = getattr(unit, "agent", None)
        return ExperimentContext(
            agent=agent,
            rng=np.random.default_rng(self.seed),
            settings=dict(self.settings),
        )

    def _run_runnable_unit(self, unit: RunnableUnitLike, ctx: ExperimentContext) -> List[Dict[str, Any]]:
        """
        v2.1 path for units implementing iter_steps(context).
        """
        unit.reset(ctx)

        records: List[Dict[str, Any]] = []
        for step in unit.iter_steps(ctx):
            record = None
            schedule = None
            metadata = getattr(step, "metadata", None)
            if isinstance(metadata, dict):
                candidate = metadata.get("record")
                if isinstance(candidate, dict):
                    record = candidate
                schedule_candidate = metadata.get("trial_schedule")
                if isinstance(schedule_candidate, TrialSchedule) or (
                    schedule_candidate is not None and hasattr(schedule_candidate, "time")
                ):
                    schedule = schedule_candidate
                elif isinstance(metadata.get("trial_time_spec"), TrialTimeSpec) or (
                    metadata.get("trial_time_spec") is not None
                    and hasattr(metadata.get("trial_time_spec"), "duration_s")
                    and hasattr(metadata.get("trial_time_spec"), "dt_s")
                ):
                    schedule = TrialSchedule(
                        time=metadata["trial_time_spec"],
                        base_stimuli=list(getattr(step.observation, "stimuli", [])),
                        available_actions=list(step.available_actions),
                    )

            if record is None:
                observation = getattr(step, "observation", None)
                context = (
                    observation.context
                    if isinstance(observation, Observation)
                    else "A"
                )
                record = {
                    "phase": "runnable_unit",
                    "trial": len(records),
                    "reward": float(getattr(step, "reward", 0.0)),
                    "context": context,
                }

            trial_id = record.get("trial", len(records))
            if schedule is not None:
                normalized_schedule = (
                    schedule
                    if isinstance(schedule, TrialSchedule)
                    else TrialSchedule(
                        time=schedule.time,
                        base_stimuli=list(getattr(schedule, "base_stimuli", [])),
                        available_actions=list(getattr(schedule, "available_actions", [])),
                        metadata=dict(getattr(schedule, "metadata", {}) or {}),
                    )
                )
                emitted = self._trial_executor.execute(
                    ctx=ctx,
                    step=step,
                    schedule=normalized_schedule,
                    base_record=record,
                    trial_id=trial_id,
                    hooks=self.hooks,
                    unit=unit,
                )
            else:
                self.hooks.on_trial_start(unit=unit, ctx=ctx, trial_id=trial_id, step=step)
                emitted = [record]
                self.hooks.on_trial_end(unit=unit, ctx=ctx, trial_id=trial_id, records=emitted)

            for emitted_record in emitted:
                finalize_record(
                    emitted_record,
                    phase_name=emitted_record.get("phase"),
                    protocol_phase_index=emitted_record.get("subphase"),
                    protocol_phase_name=emitted_record.get("subphase_name"),
                )
                self._emit_record(emitted_record)
                records.append(emitted_record)

        return records

    def _run_environment_unit(self, unit: IEnvironment, ctx: ExperimentContext) -> List[Dict[str, Any]]:
        """
        V3 path for environment-contract units implementing reset/step/done.
        """
        reset_result = unit.reset(seed=self.seed)
        _ = reset_result
        records: List[Dict[str, Any]] = []
        trial_id = 0

        while not unit.done:
            self.hooks.on_trial_start(unit=unit, ctx=ctx, trial_id=trial_id, step=None)
            step = unit.step(action=None)
            if not isinstance(step.trial_state, TrialState):
                raise TypeError("Environment step must provide typed TrialState.")
            trial_state = step.trial_state.to_dict()
            context_value = None
            z = trial_state.get("z")
            if isinstance(z, dict):
                context_value = z.get("context")

            record = {
                "phase": step.protocol,
                "trial": step.step_index,
                "tick": step.step_index,
                "stimulus": dict(step.stimulus),
                "action": step.action,
                "reward": float(step.reward),
                "done": step.done,
                "context": context_value,
                "metadata": {
                    "trial_state": trial_state,
                    "termination": step.termination.to_dict(),
                    "segment_key": step.segment_key,
                    "trial_type": step.trial_type,
                    "trial_index": step.trial_index,
                },
            }

            finalize_record(
                record,
                phase_name=step.protocol,
            )
            self._emit_record(record)
            records.append(record)
            self.hooks.on_trial_end(unit=unit, ctx=ctx, trial_id=trial_id, records=[record])
            trial_id += 1

        return records

    def run(self) -> List[Dict[str, Any]]:
        """
        Run protocols/phases to completion.

        Returns
        -------
        records : list of dict
            One record per trial, suitable for analysis.
        """
        units = self.runtime_units
        if not isinstance(units, list):
            units = [units]

        records: List[Dict[str, Any]] = []
        ctx: Optional[ExperimentContext] = self.context

        for unit in units:
            if ctx is None:
                ctx = self._build_context(unit)
            if getattr(ctx, "agent", None) is None:
                candidate_agent = getattr(unit, "agent", None)
                if candidate_agent is not None:
                    ctx.agent = candidate_agent
            self.hooks.on_unit_start(unit=unit, ctx=ctx)

            if isinstance(unit, IEnvironment):
                unit_records = self._run_environment_unit(unit, ctx)
                records.extend(unit_records)
                self.hooks.on_unit_end(unit=unit, ctx=ctx, records=unit_records)
            elif isinstance(unit, RunnableUnitLike):
                unit_records = self._run_runnable_unit(unit, ctx)
                records.extend(unit_records)
                self.hooks.on_unit_end(unit=unit, ctx=ctx, records=unit_records)
            else:
                raise TypeError(
                    f"Unsupported runtime unit: {type(unit).__name__} must implement iter_steps(context) or IEnvironment."
                )

        if self._owns_sink:
            self.sink.close()

        return records
