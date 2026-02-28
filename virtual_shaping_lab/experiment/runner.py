# experiment/runner.py

from typing import List, Dict, Any, Optional, Protocol, runtime_checkable

import numpy as np

from experiment.domain.types import ExperimentContext
from virtual_shaping_lab.domain.types import Observation
from virtual_shaping_lab.experiment.phases.series_helpers import attach_reference_stimuli
from virtual_shaping_lab.experiment.runtime_records import finalize_record


@runtime_checkable
class ProtocolLike(Protocol):
    def run(self) -> List[Dict[str, Any]]: ...


@runtime_checkable
class PhaseLike(Protocol):
    def has_next_trial(self) -> bool: ...
    def step(self) -> Dict[str, Any] | None: ...


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
    """

    def __init__(
        self,
        runtime_units,
        *,
        seed: Optional[int] = None,
        context: Optional[ExperimentContext] = None,
        settings: Optional[dict[str, Any]] = None,
    ):
        self.runtime_units = runtime_units
        self.seed = seed
        self.context = context
        self.settings = settings or {}

    def _prepare_phase_rng(self, phase: Any, ctx: ExperimentContext) -> None:
        # Respect explicit per-phase seeds when present.
        params = getattr(phase, "params", {}) or {}
        if params.get("rng_seed") is not None:
            return
        if hasattr(phase, "_rng") and getattr(phase, "_rng") is None:
            phase._rng = ctx.rng

    def _run_phase(self, phase: PhaseLike, ctx: ExperimentContext) -> List[Dict[str, Any]]:
        self._prepare_phase_rng(phase, ctx)
        records: List[Dict[str, Any]] = []
        while phase.has_next_trial():
            record = phase.step()
            if record is not None:
                finalize_record(
                    record,
                    phase_name=record.get("phase"),
                )
                records.append(record)
        return records

    def _run_protocol(self, protocol: Any, ctx: ExperimentContext) -> List[Dict[str, Any]]:
        """
        Standardized protocol execution path driven by phase stepping.

        This keeps runtime orchestration in one place while preserving
        protocol-specific phase construction logic.
        """
        if not hasattr(protocol, "build_phases"):
            return protocol.run()

        phases = protocol.build_phases()
        attach_reference_stimuli(phases)
        for phase in phases:
            self._prepare_phase_rng(phase, ctx)

        if hasattr(protocol, "_validate_phase_ordering"):
            protocol._validate_phase_ordering(phases)

        max_debug_trials = (
            protocol._max_debug_trials()
            if hasattr(protocol, "_max_debug_trials")
            else max(getattr(protocol, "n_trials", 0) * 2, 10_000)
        )

        phase_index = 0
        records: List[Dict[str, Any]] = []

        while getattr(protocol, "trial_index", 0) < getattr(protocol, "n_trials", 0):
            if getattr(protocol, "trial_index", 0) > max_debug_trials:
                raise RuntimeError(
                    f"Protocol exceeded safety limit ({max_debug_trials} trials)"
                )

            while phase_index < len(phases) and not phases[phase_index].has_next_trial():
                phase_index += 1
            if phase_index >= len(phases):
                break

            phase = phases[phase_index]
            record = phase.step()

            if record is not None:
                finalize_record(
                    record,
                    phase_name=record.get("phase"),
                    protocol_phase_index=phase_index,
                    protocol_phase_name=getattr(phase, "name", str(phase_index)),
                )
                records.append(record)

            protocol.trial_index = getattr(protocol, "trial_index", 0) + 1

            if not phase.has_next_trial():
                phase_index += 1
                if phase_index >= len(phases):
                    break

        protocol.records = records
        return records

    def _build_context(self, unit: Any) -> ExperimentContext:
        if self.context is not None:
            return self.context

        agent = getattr(unit, "agent", None)
        if agent is None and hasattr(unit, "phase"):
            agent = getattr(unit.phase, "agent", None)
        if agent is None and hasattr(unit, "protocol"):
            agent = getattr(unit.protocol, "agent", None)
        return ExperimentContext(
            agent=agent,
            rng=np.random.default_rng(self.seed),
            settings=dict(self.settings),
        )

    def _run_runnable_unit(self, unit: RunnableUnitLike, ctx: ExperimentContext) -> List[Dict[str, Any]]:
        """
        v2.1 path for units implementing iter_steps(context).
        """
        try:
            unit.reset(ctx)
        except TypeError:
            # Backward-compatible for adapters that expose reset without context.
            unit.reset()

        records: List[Dict[str, Any]] = []
        for step in unit.iter_steps(ctx):
            record = None
            metadata = getattr(step, "metadata", None)
            if isinstance(metadata, dict):
                candidate = metadata.get("record")
                if isinstance(candidate, dict):
                    record = candidate

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

            finalize_record(record, phase_name=record.get("phase"))
            records.append(record)

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

        # Attach reference stimuli across phase-mode sequences
        if units and isinstance(units[0], PhaseLike):
            attach_reference_stimuli(units)

        for unit in units:
            if ctx is None:
                ctx = self._build_context(unit)
            if getattr(ctx, "agent", None) is None:
                candidate_agent = getattr(unit, "agent", None)
                if candidate_agent is not None:
                    ctx.agent = candidate_agent

            if isinstance(unit, RunnableUnitLike):
                records.extend(self._run_runnable_unit(unit, ctx))
            elif isinstance(unit, ProtocolLike):
                records.extend(self._run_protocol(unit, ctx))
            elif isinstance(unit, PhaseLike):
                records.extend(self._run_phase(unit, ctx))
            else:
                raise TypeError(
                    f"Unsupported runtime unit: {type(unit).__name__} must implement one of: "
                    "iter_steps(context), run(), or (has_next_trial + step)."
                )

        return records
