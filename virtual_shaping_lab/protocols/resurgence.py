from typing import Any, Dict, List

from protocols.base import BaseProtocol
from experiment.phases.operant_acquisition import OperantAcquisitionPhase
from experiment.world.schedules import build_reward_schedule


class ResurgenceProtocol(BaseProtocol):
    """
    Operant resurgence-like sequence:
    reinforced response -> suppression/extinction -> recovery block.
    """

    name = "resurgence"

    def __init__(
        self,
        agent,
        stimuli: List[Any] | Dict[str, List[Any]] | None = None,
        params: Dict[str, Any] | None = None,
        **_,
    ):
        self.agent = agent
        self.stimuli = stimuli or {"cs_plus": ["lever"]}
        self.params = params or {}
        super().__init__(agent=agent, stimuli=self.stimuli, n_trials=0, params=self.params)

    def build_phases(self):
        n_acq = int(self.params.get("n_acquisition_trials", 60))
        n_supp = int(self.params.get("n_suppression_trials", 60))
        n_res = int(self.params.get("n_resurgence_trials", 40))

        acq_schedule = build_reward_schedule(
            self.params.get("acquisition_schedule", {"type": "fixed_ratio", "value": 1, "reward": 1.0})
        )
        suppression_schedule = build_reward_schedule(
            self.params.get("suppression_schedule", {"type": "fixed_ratio", "value": 1, "reward": 0.0})
        )
        resurgence_schedule = build_reward_schedule(
            self.params.get("resurgence_schedule", {"type": "fixed_ratio", "value": 1, "reward": 1.0})
        )

        acq = OperantAcquisitionPhase(
            agent=self.agent,
            stimuli=self.stimuli,
            n_trials=n_acq,
            reward_schedule=acq_schedule,
            params=self.params,
        )
        acq.name = "resurgence_acquisition"

        suppression = OperantAcquisitionPhase(
            agent=self.agent,
            stimuli=self.stimuli,
            n_trials=n_supp,
            reward_schedule=suppression_schedule,
            params=self.params,
        )
        suppression.name = "resurgence_suppression"

        resurgence = OperantAcquisitionPhase(
            agent=self.agent,
            stimuli=self.stimuli,
            n_trials=n_res,
            reward_schedule=resurgence_schedule,
            params=self.params,
        )
        resurgence.name = "resurgence_recovery"

        phases = [acq, suppression, resurgence]
        history = []
        for phase in phases:
            phase.validate(history)
            history.append(phase)

        self.n_trials = n_acq + n_supp + n_res
        return phases

