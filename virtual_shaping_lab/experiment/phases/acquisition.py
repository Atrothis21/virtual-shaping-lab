# experiment/phases/acquisition.py

from typing import Any, Dict, List

from experiment.phases.base import PhaseBase
from experiment.phases.learning_helpers import apply_attention_update
from virtual_shaping_lab.agents.representations.observation import make_observation


class AcquisitionPhase(PhaseBase):
    """
    Reinforcement phase.

    A stimulus or action predicts an outcome (US / reward).
    This phase builds associative strength.
    """

    name = "acquisition"
    allows_learning = True
    requires_prior_learning = False

    def __init__(
        self,
        agent,
        stimuli: Dict[str, List[Any]],
        n_trials: int,
        params: Dict[str, Any] | None = None,
    ):
        """
        Parameters
        ----------
        agent :
            Learning agent.
        stimuli :
            Dict with cs_plus/cs_minus.
        n_trials :
            Number of trials.
        params :
            Phase-specific settings (single source of truth).
            Advanced: outcome (US magnitude).
        """
        if not isinstance(stimuli, dict):
            raise ValueError("AcquisitionPhase expects stimuli as a dict with cs_plus/cs_minus.")

        cs_plus = stimuli.get("cs_plus", [])
        if not isinstance(cs_plus, list) or len(cs_plus) == 0:
            raise ValueError("AcquisitionPhase requires stimuli['cs_plus'] to be a non-empty list.")

        # Only train on cs_plus
        stimuli = cs_plus

        super().__init__(agent, stimuli, n_trials, params)

        # Advanced parameter: reinforcement magnitude (US)
        self.outcome = self.params.get("outcome", 1.0)

    # ------------------------------------------------------------------
    # Trial definition
    # ------------------------------------------------------------------

    def sample_trial(self) -> Dict[str, Any]:
        """
        Sample a single stimulus for the trial.
        """
        stimulus = self.stimuli[0] if len(self.stimuli) == 1 else self.stimuli[
            self.trial_index % len(self.stimuli)
        ]

        return {
            "stimulus": stimulus,
        }

    def run_trial(self, trial_spec: Dict[str, Any]) -> Any:
        """
        Deliver reinforcement.
        """
        stimulus = trial_spec["stimulus"]

        if isinstance(stimulus, tuple):
            obs = make_observation(
                stimuli=list(stimulus),
                context=self.context,
                compound=True
            )
        else:
            obs = make_observation(
                stimuli=[stimulus],
                context=self.context,
                compound=False
            )

        state = self.agent.observe(obs)
        prediction = self.agent.value(state)

        action = self.agent.act(state)

        return {
            "stimulus": stimulus,
            "action": action,
            "reward": self.outcome,
            "state": state,
            "prediction": prediction,
        }

    def apply_learning(self, trial_spec: Dict[str, Any], outcome: Any) -> None:
        """
        Apply learning via the agent.
        """
        apply_attention_update(
            self.agent,
            outcome["state"],
            outcome["reward"],
            outcome.get("action"),
            cue_labels=outcome.get("stimulus"),
        )

    def record_trial(
        self,
        trial_spec: Dict[str, Any],
        outcome: Any,
    ) -> Dict[str, Any]:
        """
        Record acquisition trial.
        """
        stimulus = outcome["stimulus"]
        return {
            "phase": self.name,
            "trial": self.trial_index,
            "stimulus": stimulus,
            "action": outcome["action"],
            "response": outcome["action"] if outcome["action"] is not None else outcome["prediction"],
            "reward": outcome["reward"],
            "prediction": outcome["prediction"],
            "a_stimulus": stimulus,
            "b_stimulus": None,
            "series_labels": {"label_1": "CS1", "label_2": "CS2"},
            "series_values": {"CS1": outcome["prediction"], "CS2": None},
        }


