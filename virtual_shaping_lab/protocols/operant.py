# protocols/operant.py

from typing import Any, Dict, List

from protocols.base import BaseProtocol
from experiment.phases.operant_acquisition import OperantAcquisitionPhase
from experiment.factories.reward_schedule_factory import build_reward_schedule


CONSEQUENCE_DEFAULT_REWARD = {
    "positive_reinforcement": 1.0,
    "negative_reinforcement": 1.0,
    "positive_punishment": -1.0,
    "negative_punishment": -1.0,
}


class OperantConditioningProtocol(BaseProtocol):
    """
    Operant conditioning protocol.

    Implemented as a single OperantAcquisitionPhase.
    All parameters are read from params.
    """

    name = "operant_conditioning"

    def __init__(
        self,
        agent,
        stimuli: List[Any] | None = None,
        params: Dict[str, Any] | None = None,
        **_
    ):
        self.agent = agent
        self.stimuli = stimuli or []
        self.params = params or {}

        super().__init__(
            agent=agent,
            stimuli=self.stimuli,
            n_trials=0,
            params=self.params,
        )

    def _resolve_consequence_mode(self) -> str:
        mode = self.params.get("consequence_mode", "positive_reinforcement")
        if mode not in CONSEQUENCE_DEFAULT_REWARD:
            raise ValueError(
                "operant_conditioning params.consequence_mode must be one of: "
                + ", ".join(sorted(CONSEQUENCE_DEFAULT_REWARD.keys()))
            )
        return mode

    def _resolve_reward_schedule(self, consequence_mode: str):
        schedule = self.params.get("reward_schedule")
        if schedule is None:
            schedule = {"type": "fixed_ratio", "value": 1}

        # Assemble may already build a concrete schedule object.
        if hasattr(schedule, "step"):
            return schedule

        if not isinstance(schedule, dict):
            raise TypeError("operant_conditioning params.reward_schedule must be an object")

        reward = float(schedule.get("reward", CONSEQUENCE_DEFAULT_REWARD[consequence_mode]))
        if consequence_mode in {"positive_reinforcement", "negative_reinforcement"}:
            reward = abs(reward)
            if reward == 0.0:
                reward = 1.0
        else:
            reward = -abs(reward)
            if reward == 0.0:
                reward = -1.0

        schedule_cfg = {**schedule, "reward": reward}
        return build_reward_schedule(schedule_cfg)

    def build_phases(self):
        n_trials = int(self.params.get("n_trials", 100))
        consequence_mode = self._resolve_consequence_mode()
        reward_schedule = self._resolve_reward_schedule(consequence_mode)

        phase = OperantAcquisitionPhase(
            agent=self.agent,
            stimuli=self.stimuli,
            n_trials=n_trials,
            reward_schedule=reward_schedule,
            params={
                **self.params,
                "consequence_mode": consequence_mode,
            },
        )

        phase.validate(history=None)

        self.n_trials = n_trials
        return [phase]
