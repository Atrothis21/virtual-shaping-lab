# experiment/phases/operant_acquisition.py

from typing import Any, Dict, List

from experiment.phases.base import PhaseBase
from experiment.phases.learning_helpers import apply_attention_update
from agents.representations.observation import make_observation


def _classify_operant_outcome(reward: float) -> str:
    if reward > 0:
        return "reinforcement"
    if reward < 0:
        return "punishment"
    return "extinction"


class OperantAcquisitionPhase(PhaseBase):
    """
    Operant acquisition phase.

    Reinforcement is delivered according to a reward schedule
    contingent on the agent's emitted actions.
    """

    name = "operant_acquisition"
    allows_learning = True
    requires_prior_learning = False

    def __init__(
        self,
        agent,
        stimuli: Dict[str, List[Any]] | List[Any],
        n_trials: int,
        reward_schedule,
        params: Dict[str, Any] | None = None,
    ):
        # Normalize stimuli if provided as dict
        if isinstance(stimuli, dict):
            cs_plus = stimuli.get("cs_plus", [])
            stimuli = cs_plus if isinstance(cs_plus, list) else []
        elif stimuli is None:
            stimuli = []

        super().__init__(
            agent=agent,
            stimuli=stimuli,
            n_trials=n_trials,
            params=params,
        )

        self.reward_schedule = reward_schedule

        if hasattr(self.reward_schedule, "reset"):
            self.reward_schedule.reset()

        if hasattr(self.agent, "reset"):
            self.agent.reset()

    # ------------------------------------------------------------------
    # Trial definition
    # ------------------------------------------------------------------

    def sample_trial(self) -> Dict[str, Any]:
        """
        Operant trials do not require stimulus sampling.
        """
        return {}

    def run_trial(self, trial_spec: Dict[str, Any]) -> Any:
        """
        Select action and compute reward from schedule.
        """
        observation = self.stimuli[0] if self.stimuli else "operant"
        obs = make_observation(
            stimuli=[observation],
            context=self.context,
            compound=False
        )
        state = self.agent.observe(obs)
        prediction = self.agent.value(state)
        action = self.agent.act(state)

        reward = float(self.reward_schedule.step(
            action=action,
            t=self.trial_index,
        ))

        return {
            "action": action,
            "reward": reward,
            "outcome_type": _classify_operant_outcome(reward),
            "state": state,
            "prediction": prediction,
        }

    def apply_learning(self, trial_spec: Dict[str, Any], outcome: Any) -> None:
        """
        In operant learning, the action itself serves as the learning state.
        """
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
        """
        Record operant trial.
        """
        return {
            "phase": self.name,
            "trial": self.trial_index,
            "stimulus": None,
            "action": outcome["action"],
            "response": outcome["action"] if outcome["action"] is not None else outcome["prediction"],
            "reward": outcome["reward"],
            "outcome_type": outcome.get("outcome_type", _classify_operant_outcome(float(outcome["reward"]))),
            "prediction": outcome["prediction"],
            "schedule": getattr(self.reward_schedule, "name", None),
        }

