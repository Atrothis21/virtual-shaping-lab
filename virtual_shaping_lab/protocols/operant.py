# protocols/operant.py

from typing import Any, Dict, List

from protocols.base import BaseProtocol
from experiment.phases.operant_acquisition import OperantAcquisitionPhase


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

    def build_phases(self):
        n_trials = self.params.get("n_trials", 100)
        reward_schedule = self.params.get("reward_schedule")

        phase = OperantAcquisitionPhase(
            agent=self.agent,
            stimuli=self.stimuli,
            n_trials=n_trials,
            reward_schedule=reward_schedule,
            params=self.params,
        )

        phase.validate(history=None)

        self.n_trials = n_trials
        return [phase]
