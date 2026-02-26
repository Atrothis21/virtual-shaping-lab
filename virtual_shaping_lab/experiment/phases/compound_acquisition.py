# experiment/phases/compound_acquisition.py

from typing import Any, Dict, List

from experiment.phases.base import PhaseBase
from experiment.phases.series_helpers import make_dual_series
from virtual_shaping_lab.agents.representations.observation import make_observation


class CompoundAcquisitionPhase(PhaseBase):
    """
    Compound acquisition phase.

    A compound stimulus (e.g., A + B) predicts reinforcement.
    This phase supports overshadowing, blocking, and summation effects
    depending on prior phase history.
    """

    name = "compound_acquisition"
    allows_learning = True
    requires_prior_learning = False

    def __init__(
        self,
        agent,
        stimuli: Dict[str, List[Any]],
        n_trials: int,
        outcome: float = 1.0,
        params: Dict[str, Any] | None = None,
    ):
        """
        Parameters
        ----------
        agent :
            Learning agent.
        stimuli :
            Dict with key {"compound"} mapping to a list of 2 stimuli.
            Example: {"compound": [A, X]}
        n_trials :
            Number of compound acquisition trials.
        outcome :
            Reinforcement magnitude.
        """
        # Enforce dict-only stimuli with compound key
        if not isinstance(stimuli, dict):
            raise ValueError("CompoundAcquisitionPhase expects stimuli as a dict with key 'compound'.")

        compound = stimuli.get("compound", [])
        if not isinstance(compound, list) or len(compound) < 2:
            raise ValueError("CompoundAcquisitionPhase requires stimuli['compound'] with at least two items.")

        super().__init__(
            agent=agent,
            stimuli=compound,
            n_trials=n_trials,
            params=params,
        )

        self.outcome = outcome

    # ------------------------------------------------------------------
    # Trial definition
    # ------------------------------------------------------------------

    def sample_trial(self) -> Dict[str, Any]:
        """
        Present the full compound on every trial.
        """
        return {
            "compound": tuple(self.stimuli),
        }

    def run_trial(self, trial_spec: Dict[str, Any]) -> Any:
        """
        Present compound stimulus and deliver reinforcement.
        """
        compound = trial_spec["compound"]
        a = compound[0]
        b = compound[1]

        # Observe compound (actual trial)
        obs = make_observation(
            stimuli=list(compound),
            context=self.context,
            compound=True
        )
        state = self.agent.observe(obs)

        # Compute A/B predictions without mutating agent internal state
        obs_a = make_observation(
            stimuli=[a],
            context=self.context,
            compound=False
        )
        obs_b = make_observation(
            stimuli=[b],
            context=self.context,
            compound=False
        )

        state_a = self.agent.representation.encode(obs_a)
        state_b = self.agent.representation.encode(obs_b)

        a_prediction = self.agent.value(state_a)
        b_prediction = self.agent.value(state_b)

        prediction = self.agent.value(state)
        action = self.agent.act(state)

        return {
            "compound": compound,
            "action": action,
            "reward": self.outcome,
            "state": state,
            "prediction": prediction,
            "a_prediction": a_prediction,
            "b_prediction": b_prediction,
            "a_stimulus": a,
            "b_stimulus": b,
            "state_a": state_a,
            "state_b": state_b,
            "prediction_by_stimulus": {
                a: a_prediction,
                b: b_prediction,
                "compound": prediction
            }
        }

    def apply_learning(self, trial_spec: Dict[str, Any], outcome: Any) -> None:
        """
        Apply cue-specific learning using shared compound prediction error.
        """
        alpha_cs1 = self.params.get("alpha_cs1", self.agent.learner.alpha)
        alpha_cs2 = self.params.get("alpha_cs2", self.agent.learner.alpha)

        attention_map = getattr(self.agent.learner, "attention_map", {}) or {}
        stim_a = outcome.get("a_stimulus")
        stim_b = outcome.get("b_stimulus")
        alpha_cs1 = alpha_cs1 * float(attention_map.get(stim_a, 1.0))
        alpha_cs2 = alpha_cs2 * float(attention_map.get(stim_b, 1.0))

        state_a = outcome.get("state_a")
        state_b = outcome.get("state_b")

        reward = outcome["reward"]
        action = outcome.get("action")

        # Shared compound prediction error
        delta = (reward - outcome["prediction"]) / 2

        self.agent.learner.update_with_alpha(state_a, reward, action, alpha_cs1, delta_override=delta)
        self.agent.learner.update_with_alpha(state_b, reward, action, alpha_cs2, delta_override=delta)

    def record_trial(
        self,
        trial_spec: Dict[str, Any],
        outcome: Any,
    ) -> Dict[str, Any]:
        """
        Record compound acquisition trial.
        """
        series = make_dual_series(
            "CS1", outcome.get("a_prediction"),
            "CS2", outcome.get("b_prediction"),
        )

        return {
            "phase": self.name,
            "trial": self.trial_index,
            "stimulus": outcome["compound"],
            "stimulus_type": "compound",
            "stimulus_components": list(outcome["compound"]),
            "compound": outcome["compound"],
            "action": outcome["action"],
            "response": outcome["action"] if outcome["action"] is not None else outcome["prediction"],
            "reward": outcome["reward"],
            "prediction": outcome["prediction"],
            "a_prediction": outcome.get("a_prediction"),
            "b_prediction": outcome.get("b_prediction"),
            "a_stimulus": outcome.get("a_stimulus"),
            "b_stimulus": outcome.get("b_stimulus"),
            "prediction_by_stimulus": outcome.get("prediction_by_stimulus"),
            **series,
            "compound_series": {
                "label": "AX",
                "value": outcome.get("prediction")
            },
        }



