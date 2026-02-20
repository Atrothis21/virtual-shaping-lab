# experiment/phases/differential_acquisition.py

import random
from typing import Any, Dict, List

from experiment.phases.base import PhaseBase
from experiment.phases.learning_helpers import apply_attention_update
from experiment.phases.series_helpers import make_dual_series
from agents.representations.observation import make_observation


class DifferentialAcquisitionPhase(PhaseBase):
    """
    Differential conditioning phase.

    CS+ trials are reinforced.
    CS- trials are not reinforced.

    Learning occurs for both stimulus types within a single phase.
    """

    name = "differential_acquisition"
    allows_learning = True
    requires_prior_learning = False

    def __init__(
        self,
        agent,
        stimuli: Dict[str, List[Any]],
        n_trials: int,
        reinforced_outcome: float = 1.0,
        params: Dict[str, Any] | None = None,
    ):
        """
        Parameters
        ----------
        agent :
            Learning agent.
        stimuli :
            Dict with keys {"cs_plus", "cs_minus"} mapping to stimulus lists.
        n_trials :
            Total number of trials.
        reinforced_outcome :
            Reward magnitude for CS+ trials.
        """
        # Enforce dict-only stimuli
        if not isinstance(stimuli, dict):
            raise ValueError(
                "DifferentialAcquisitionPhase expects stimuli as a dict "
                "with keys {'cs_plus', 'cs_minus'}"
            )

        if not {"cs_plus", "cs_minus"} <= stimuli.keys():
            raise ValueError(
                "DifferentialAcquisitionPhase requires "
                "stimuli with keys {'cs_plus', 'cs_minus'}"
            )

        if not stimuli["cs_plus"] or not stimuli["cs_minus"]:
            raise ValueError(
                "DifferentialAcquisitionPhase requires non-empty cs_plus and cs_minus lists"
            )

        super().__init__(agent, stimuli=[], n_trials=n_trials, params=params)

        self.stimuli_by_type = stimuli
        self.reinforced_outcome = reinforced_outcome

    # ------------------------------------------------------------------
    # Trial definition
    # ------------------------------------------------------------------

    def sample_trial(self) -> Dict[str, Any]:
        """
        Alternate CS+ and CS- deterministically.
        """
        stimulus_type = "cs_plus" if self.trial_index % 2 == 0 else "cs_minus"
        stimulus = random.choice(self.stimuli_by_type[stimulus_type])

        return {
            "stimulus": stimulus,
            "stimulus_type": stimulus_type,
        }

    def run_trial(self, trial_spec: Dict[str, Any]) -> Any:
        stimulus = trial_spec["stimulus"]
        stimulus_type = trial_spec["stimulus_type"]

        obs = make_observation(
            stimuli=[stimulus],
            context=self.context,
            compound=False
        )
        state = self.agent.observe(obs)
        prediction = self.agent.value(state)
        action = self.agent.act(state)

        reward = self.reinforced_outcome if stimulus_type == "cs_plus" else 0.0

        return {
            "stimulus": stimulus,
            "stimulus_type": stimulus_type,
            "action": action,
            "reward": reward,
            "state": state,
            "prediction": prediction,
        }

    def apply_learning(self, trial_spec: Dict[str, Any], outcome: Any) -> None:
        apply_attention_update(
            self.agent,
            outcome["state"],
            outcome["reward"],
            outcome.get("action")
        )

    def record_trial(
        self,
        trial_spec: Dict[str, Any],
        outcome: Any,
    ) -> Dict[str, Any]:
        cs_plus_val = outcome["prediction"] if outcome["stimulus_type"] == "cs_plus" else None
        cs_minus_val = outcome["prediction"] if outcome["stimulus_type"] == "cs_minus" else None

        series = make_dual_series(
            "CS+", cs_plus_val,
            "CS-", cs_minus_val,
        )

        return {
            "phase": self.name,
            "trial": self.trial_index,
            "stimulus": outcome["stimulus"],
            "stimulus_type": outcome["stimulus_type"],
            "action": outcome["action"],
            "response": outcome["action"] if outcome["action"] is not None else outcome["prediction"],
            "reward": outcome["reward"],
            "prediction": outcome["prediction"],
            **series,
        }

