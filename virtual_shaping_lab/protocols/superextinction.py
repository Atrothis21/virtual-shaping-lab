from typing import Any, Dict, List

from protocols.base import BaseProtocol
from experiment.phases.operant_acquisition import OperantAcquisitionPhase
from experiment.world.schedules import build_reward_schedule


class SuperextinctionProtocol(BaseProtocol):
    """
    Operant superextinction sequence:
    reinforced response followed by explicit punishment block.
    """

    name = "superextinction"

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
        n_acq = int(self.params.get("n_acquisition_trials", 80))
        n_super = int(self.params.get("n_superextinction_trials", 80))

        acq_schedule = build_reward_schedule(
            self.params.get("acquisition_schedule", {"type": "fixed_ratio", "value": 1, "reward": 1.0})
        )
        superextinction_schedule = build_reward_schedule(
            self.params.get("superextinction_schedule", {"type": "fixed_ratio", "value": 1, "reward": -1.0})
        )

        acq = OperantAcquisitionPhase(
            agent=self.agent,
            stimuli=self.stimuli,
            n_trials=n_acq,
            reward_schedule=acq_schedule,
            params=self.params,
        )
        acq.name = "superextinction_acquisition"

        superext = OperantAcquisitionPhase(
            agent=self.agent,
            stimuli=self.stimuli,
            n_trials=n_super,
            reward_schedule=superextinction_schedule,
            params=self.params,
        )
        superext.name = "superextinction_phase"

        phases = [acq, superext]
        history = []
        for phase in phases:
            phase.validate(history)
            history.append(phase)

        self.n_trials = n_acq + n_super
        return phases

