# protocols/base.py

import random
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

import numpy as np

from experiment.phases.series_helpers import attach_reference_stimuli
from protocols.step_adapter import ProtocolStepAdapter
from virtual_shaping_lab.experiment.domain.types import ExperimentContext, StepResult


class BaseProtocol(ABC):
    """
    Base class for all experimental protocols.

    Protocols are behavioral-phenomena orchestrators:
    they ONLY compose and order canonical phases.
    All trial logic lives in phases.

    Protocols should read all protocol-specific settings from `params`.
    Do not add protocol-specific kwargs; keep the constructor uniform.
    """

    name: str = "base"

    def __init__(
        self,
        agent,
        stimuli: Any = None,
        n_trials: int = 0,
        params: Optional[Dict[str, Any]] = None,
    ):
        """
        Parameters
        ----------
        agent :
            Shared agent instance.
        stimuli :
            Optional protocol-level stimulus specification.
        n_trials :
            Optional initial total trial count (protocols may override).
        params :
            Protocol-specific settings (single source of truth).
        """
        self.agent = agent
        self.stimuli = stimuli
        self.n_trials = n_trials
        self.params = params or {}

        self.trial_index: int = 0
        self.records: List[Dict[str, Any]] = []
        self._step_adapter = ProtocolStepAdapter(self.name)

    # ------------------------------------------------------------------
    # Required protocol hook
    # ------------------------------------------------------------------

    @abstractmethod
    def build_phases(self) -> List[Any]:
        """
        Return an ordered list of phase instances.
        Subclasses enforce ordering and parameterization here.
        """
        raise NotImplementedError

    # ------------------------------------------------------------------
    # Optional validation hook
    # ------------------------------------------------------------------

    def validate(self, history: Optional[List["BaseProtocol"]] = None) -> None:
        """
        Protocol-level validation (default: none).
        """
        return None

    # ------------------------------------------------------------------
    # Execution control
    # ------------------------------------------------------------------

    def has_next_trial(self) -> bool:
        return self.trial_index < self.n_trials

    def run(self) -> List[Dict[str, Any]]:
        """
        Execute the protocol by stepping through composed phases.
        """
        ctx = ExperimentContext(agent=self.agent, rng=np.random.default_rng())
        for _ in self.iter_steps(ctx):
            pass
        return self.records

    def iter_steps(self, ctx: ExperimentContext):
        """
        Runnable-unit contract: protocol composes child runnable units only.
        """
        max_debug_trials = self._max_debug_trials()
        phases = self.build_phases()
        attach_reference_stimuli(phases)
        self._validate_phase_ordering(phases)
        for phase_index, phase in enumerate(phases):
            self._check_safety_limit(max_debug_trials)
            if not hasattr(phase, "iter_steps"):
                raise TypeError(
                    f"Protocol child unit '{type(phase).__name__}' must implement iter_steps(context)."
                )
            if hasattr(phase, "reset"):
                phase.reset(ctx)

            phase_name = getattr(phase, "name", str(phase_index))

            for step in phase.iter_steps(ctx):
                self._check_safety_limit(max_debug_trials)
                if not self.has_next_trial():
                    return
                yield self._step_adapter.adapt(
                    step=step,
                    phase_name=phase_name,
                    phase_index=phase_index,
                    is_last_phase=(phase_index == len(phases) - 1),
                    trial_index=self.trial_index,
                    n_trials=self.n_trials,
                    records_sink=self.records,
                )
                self.trial_index += 1

    # ------------------------------------------------------------------
    # Reference stimulus helpers (plot continuity)
    # ------------------------------------------------------------------

    # ------------------------------------------------------------------

    # ------------------------------------------------------------------
    # Utilities
    # ------------------------------------------------------------------

    def _validate_phase_ordering(self, phases: List[Any]) -> None:
        history: List[Any] = []
        for phase in phases:
            phase.validate(history)
            history.append(phase)

    def _max_debug_trials(self) -> int:
        return max(self.n_trials * 2, 10_000)

    def _check_safety_limit(self, max_debug_trials: int) -> None:
        if self.trial_index > max_debug_trials:
            raise RuntimeError(
                f"Protocol exceeded safety limit "
                f"({max_debug_trials} trials)"
            )

    def reset(self, ctx: Optional[ExperimentContext] = None) -> None:
        self.trial_index = 0
        self.records = []
        if hasattr(self.agent, "reset"):
            self.agent.reset()

    def get_protocol_summary(self) -> Dict[str, Any]:
        return {}

    # ------------------------------------------------------------------
    # Legacy stimulus helper (optional)
    # ------------------------------------------------------------------

    def sample_stimulus(self):
        if not isinstance(self.stimuli, dict):
            raise ValueError(
                "sample_stimulus expects stimuli to be a dict "
                "mapping stimulus_type -> list[stimulus]"
            )

        valid_types = [
            stimulus_type
            for stimulus_type, values in self.stimuli.items()
            if isinstance(values, list) and len(values) > 0
        ]

        if not valid_types:
            raise ValueError(
                "No valid stimuli available to sample "
                "(all stimulus lists are empty)"
            )

        stimulus_type = random.choice(valid_types)
        stimulus = random.choice(self.stimuli[stimulus_type])

        return stimulus, stimulus_type
