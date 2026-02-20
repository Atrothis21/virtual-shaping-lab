# experiment/phases/context_shift.py

from typing import Any, Dict, List

from experiment.phases.base import PhaseBase


class ContextShiftPhase(PhaseBase):
    """
    Context shift phase.

    Sets a contextual state under which subsequent stimulus-response
    learning or performance occurs.

    This phase does not introduce new contingencies by itself;
    it modifies the background conditions of learning or retrieval.
    """

    name = "context_shift"
    allows_learning = False
    requires_prior_learning = False

    def __init__(
        self,
        agent,
        context: Any | None = None,
        stimuli: List[Any] | None = None,
        n_trials: int = 0,
        params: Dict[str, Any] | None = None,
    ):
        # Force zero-trial context shift
        n_trials = 0
        super().__init__(
            agent=agent,
            stimuli=stimuli or [],
            n_trials=n_trials,
            params=params,
        )

        self.context = context or self.params.get("context", "A")

    # ------------------------------------------------------------------
    # Trial definition
    # ------------------------------------------------------------------

    def sample_trial(self) -> Dict[str, Any]:
        """
        Context shifts do not produce trials.
        """
        return {}

    def run_trial(self, trial_spec: Dict[str, Any]) -> Any:
        """
        No-op: context shifts do not emit trials.
        """
        return {
            "context": self.context,
            "stimulus": None,
            "action": None,
            "reward": 0.0,
            "state": None,
            "prediction": 0.0,
        }

    def apply_learning(self, trial_spec: Dict[str, Any], outcome: Any) -> None:
        """
        Learning is disabled during context shifts.
        """
        return None

    def record_trial(
        self,
        trial_spec: Dict[str, Any],
        outcome: Any,
    ) -> Dict[str, Any]:
        """
        Record contextual shift (if ever called).
        """
        return {
            "phase": self.name,
            "trial": self.trial_index,
            "context": self.context,
            "stimulus": None,
            "action": None,
            "response": 0.0,
            "reward": 0.0,
            "prediction": 0.0,
        }
