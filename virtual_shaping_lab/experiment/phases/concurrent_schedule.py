# experiment/phases/concurrent_schedule.py

from typing import Any, Dict, List

from experiment.phases.base import PhaseBase
from experiment.phases.learning_helpers import apply_attention_update
from experiment.factories.reward_schedule_factory import build_reward_schedule
from agents.representations.observation import make_observation


def _classify_operant_outcome(reward: float) -> str:
    if reward > 0:
        return "reinforcement"
    if reward < 0:
        return "punishment"
    return "extinction"


class ConcurrentSchedulePhase(PhaseBase):
    """
    Concurrent operant schedules for matching law.

    Two actions compete for reinforcement, each governed by its own schedule.
    """

    name = "concurrent_schedule"
    allows_learning = True
    requires_prior_learning = False

    def __init__(
        self,
        agent,
        n_trials: int,
        schedule_left: Dict[str, Any],
        schedule_right: Dict[str, Any],
        params: Dict[str, Any] | None = None,
        stimuli: List[Any] | None = None,
    ):
        params = params or {}

        super().__init__(
            agent=agent,
            stimuli=stimuli or ["operant"],
            n_trials=n_trials,
            params=params,
        )

        self.schedule_left = build_reward_schedule(schedule_left)
        self.schedule_right = build_reward_schedule(schedule_right)

        self.action_labels = params.get("action_labels") or ["left", "right"]
        if len(self.action_labels) != 2:
            self.action_labels = ["left", "right"]
        self.left_action = self.action_labels[0]
        self.right_action = self.action_labels[1]

        if hasattr(self.schedule_left, "reset"):
            self.schedule_left.reset()
        if hasattr(self.schedule_right, "reset"):
            self.schedule_right.reset()
        if hasattr(self.agent, "reset"):
            self.agent.reset()

    # ------------------------------------------------------------------
    # Trial definition
    # ------------------------------------------------------------------

    def sample_trial(self) -> Dict[str, Any]:
        return {}

    def run_trial(self, trial_spec: Dict[str, Any]) -> Any:
        observation = None
        if isinstance(self.stimuli, list) and self.stimuli:
            observation = self.stimuli[0]
        elif isinstance(self.stimuli, dict):
            cs_plus = self.stimuli.get("cs_plus")
            if isinstance(cs_plus, list) and cs_plus:
                observation = cs_plus[0]
        if observation is None:
            observation = "operant"
        obs = make_observation(
            stimuli=[observation],
            context=self.context,
            compound=False
        )
        state = self.agent.observe(obs)
        prediction = self.agent.value(state)
        action = self.agent.act(state)
        action_index = None
        if action == self.left_action:
            action_index = 0
        elif action == self.right_action:
            action_index = 1

        reward = 0.0
        reward_action = None
        if action_index == 0:
            reward = float(self.schedule_left.step(action=action, t=self.trial_index))
            reward_action = 0 if reward != 0 else None
        elif action_index == 1:
            reward = float(self.schedule_right.step(action=action, t=self.trial_index))
            reward_action = 1 if reward != 0 else None

        return {
            "action": action,
            "action_index": action_index,
            "reward": reward,
            "outcome_type": _classify_operant_outcome(reward),
            "reward_action": reward_action,
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
        action = outcome.get("action")
        action_index = outcome.get("action_index")
        action_label = None
        if action_index in (0, 1):
            action_label = self.action_labels[action_index]

        return {
            "phase": self.name,
            "trial": self.trial_index,
            "stimulus": None,
            "action": action_index,
            "action_raw": action,
            "action_label": action_label,
            "reward_action": outcome.get("reward_action"),
            "response": action_index if action_index is not None else outcome["prediction"],
            "reward": outcome["reward"],
            "outcome_type": outcome.get("outcome_type", _classify_operant_outcome(float(outcome["reward"]))),
            "prediction": outcome["prediction"],
            "schedule_left": getattr(self.schedule_left, "name", None),
            "schedule_right": getattr(self.schedule_right, "name", None),
        }
