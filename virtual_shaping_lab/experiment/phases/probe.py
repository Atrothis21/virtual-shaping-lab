# experiment/phases/probe.py

from typing import Any, Dict, List

from experiment.phases.base import PhaseBase
from virtual_shaping_lab.agents.representations.observation import make_observation


class ProbePhase(PhaseBase):
    """
    Probe (test) phase.

    Responding is measured without learning.
    Reinforcement may or may not occur, but no learning updates are applied.

    This phase cleanly separates performance from learning.
    """

    name = "probe"
    allows_learning = False
    requires_prior_learning = True

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
            Dict with keys {"cs_plus", "cs_minus"}.
        n_trials :
            Number of probe trials.
        deliver_reward :
            Whether reward is delivered during probe trials.
            Learning is still disabled regardless.
        reward_value :
            Reward magnitude if deliver_reward is True.
        """
        # Enforce dict-only stimuli
        if not isinstance(stimuli, dict):
            raise ValueError("ProbePhase expects stimuli as a dict with cs_plus/cs_minus.")

        cs_plus = stimuli.get("cs_plus", [])
        if not isinstance(cs_plus, list) or len(cs_plus) == 0:
            raise ValueError("ProbePhase requires stimuli['cs_plus'] to be a non-empty list.")

        # Use cs_plus list for probing
        stimuli = cs_plus

        super().__init__(
            agent=agent,
            stimuli=stimuli,
            n_trials=n_trials,
            params=params,
        )

        self.deliver_reward = bool(self.params.get("deliver_reward", False))
        self.reward_value = float(self.params.get("reward_value", 0.0))

    # ------------------------------------------------------------------
    # Trial definition
    # ------------------------------------------------------------------

    def sample_trial(self) -> Dict[str, Any]:
        """
        Cycle deterministically through probe stimuli.
        """
        stimulus = self.stimuli[self.trial_index % len(self.stimuli)]

        return {
            "stimulus": stimulus,
        }

    def run_trial(self, trial_spec: Dict[str, Any]) -> Any:
        """
        Present probe stimulus and optionally deliver reward.
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

        reward = self.reward_value if self.deliver_reward else 0.0

        return {
            "stimulus": stimulus,
            "action": action,
            "reward": reward,
            "state": state,
            "prediction": prediction,
        }

    def apply_learning(self, trial_spec: Dict[str, Any], outcome: Any) -> None:
        """
        Learning is disabled during probes.
        """
        return None

    def record_trial(
        self,
        trial_spec: Dict[str, Any],
        outcome: Any,
    ) -> Dict[str, Any]:
        """
        Record probe trial.
        """
        return {
            "phase": self.name,
            "trial": self.trial_index,
            "stimulus": outcome["stimulus"],
            "action": outcome["action"],
            "response": outcome["action"] if outcome["action"] is not None else outcome["prediction"],
            "reward": outcome["reward"],
            "prediction": outcome["prediction"],
            "series_labels": {"label_1": "CS1", "label_2": "CS2"},
            "series_values": {"CS1": outcome["prediction"], "CS2": None},
        }


