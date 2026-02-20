# experiment/phases/base.py

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, TypeAlias


TrialSpec: TypeAlias = Dict[str, Any]
TrialOutcome: TypeAlias = Any
TrialRecord: TypeAlias = Dict[str, Any]


class PhaseBase(ABC):
    """
    Base class for all experimental phases.

    A Phase defines a contiguous block of trials with fixed
    contingencies, stimulus availability, and learning permissions.

    Phases do NOT:
        - define learning rules
        - define action-selection policies
        - define experimental ordering (protocols do that)

    Phases DO:
        - define what occurs on a trial
        - define whether learning is enabled
        - define what is recorded
    """

    # ---- Phase metadata (override in subclasses) ----
    name: str = "base"
    allows_learning: bool = True
    requires_prior_learning: bool = False

    def __init__(
        self,
        agent,
        stimuli: Optional[List[Any]] = None,
        n_trials: int = 0,
        params: Optional[Dict[str, Any]] = None,
    ):
        """
        Parameters
        ----------
        agent :
            The agent interacting with the phase. The agent encapsulates
            representation, learner, and policy.
        stimuli :
            List of stimuli available in this phase.
        n_trials :
            Number of trials in the phase.
        params :
            Phase-specific settings (single source of truth for phase behavior).
        """
        self.agent = agent
        self.stimuli = stimuli or []
        self.n_trials = n_trials
        self.params = params or {}
        self.context = self.params.get("context", "A")
        self.trial_index: int = 0
        self.records: List[Dict[str, Any]] = []

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    def validate(self, history: Optional[List["PhaseBase"]] = None) -> None:
        """
        Validate whether this phase is scientifically admissible
        given the preceding phase history.

        Parameters
        ----------
        history :
            List of previously executed phases.

        Raises
        ------
        ValueError
            If the phase violates scientific constraints.
        """
        if self.requires_prior_learning and not history:
            raise ValueError(
                f"Phase '{self.name}' requires prior learning, "
                "but no prior phases were provided."
            )

    # ------------------------------------------------------------------
    # Execution control
    # ------------------------------------------------------------------

    def has_next_trial(self) -> bool:
        """Return True if trials remain in this phase."""
        return self.trial_index < self.n_trials

    def step(self) -> Optional[TrialRecord]:
        """
        Execute a single trial of the phase.

        Returns
        -------
        record : dict or None
            A serializable record of the trial.
        """
        if not self.has_next_trial():
            return None

        trial_spec = self.sample_trial()
        outcome = self.run_trial(trial_spec)

        if self.allows_learning:
            self.apply_learning(trial_spec, outcome)

        record = self.record_trial(trial_spec, outcome)
        if record is None:
            return None
        if not isinstance(record, dict):
            raise TypeError(
                f"{self.__class__.__name__}.record_trial must return a dict, "
                f"got {type(record).__name__}"
            )

        self._add_context_metadata(record)
        self.records.append(record)

        self.trial_index += 1
        return record

    # ------------------------------------------------------------------
    # Required phase hooks
    # ------------------------------------------------------------------

    @abstractmethod
    def sample_trial(self) -> TrialSpec:
        """
        Define the stimuli and/or actions available on this trial.

        Returns
        -------
        trial_spec : dict
            A structured description of the trial.
        """
        pass

    @abstractmethod
    def run_trial(self, trial_spec: TrialSpec) -> TrialOutcome:
        """
        Execute agent-environment interaction for the trial.

        Returns
        -------
        outcome :
            The outcome of the trial (e.g., reward, US, omission).
        """
        pass

    @abstractmethod
    def apply_learning(self, trial_spec: TrialSpec, outcome: TrialOutcome) -> None:
        """
        Delegate learning to the agent.

        This method should call agent.observe / agent.learn
        as appropriate.
        """
        pass

    @abstractmethod
    def record_trial(
        self,
        trial_spec: TrialSpec,
        outcome: TrialOutcome,
    ) -> TrialRecord:
        """
        Produce a serializable record of the trial.

        Returns
        -------
        record : dict
            Must be JSON-serializable.
        """
        pass

    # ------------------------------------------------------------------
    # Optional summaries
    # ------------------------------------------------------------------

    def _add_context_metadata(self, record: TrialRecord) -> None:
        record.setdefault("context", self.context)
        if hasattr(self, "context_source"):
            record.setdefault("context_source", self.context_source)
            if self.context_source == "inferred":
                record.setdefault("inferred_context", self.context)

    def get_phase_summary(self) -> Dict[str, Any]:
        """
        Optional phase-level summary statistics.
        """
        return {}
