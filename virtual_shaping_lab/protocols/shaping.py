from typing import Any, Dict, List

from protocols.base import BaseProtocol
from experiment.phases.operant_acquisition import OperantAcquisitionPhase
from experiment.world.schedules import build_reward_schedule


class ShapingProtocol(BaseProtocol):
    """
    Operant shaping protocol.

    Builds behavior through two reinforcement stages with increasing schedule demand.
    """

    name = "shaping"

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
        n_stage_1 = int(self.params.get("n_stage_1_trials", 80))
        n_stage_2 = int(self.params.get("n_stage_2_trials", 120))

        schedule_stage_1 = build_reward_schedule(
            self.params.get("schedule_stage_1", {"type": "fixed_ratio", "value": 1, "reward": 1.0})
        )
        schedule_stage_2 = build_reward_schedule(
            self.params.get("schedule_stage_2", {"type": "fixed_ratio", "value": 5, "reward": 1.0})
        )

        stage_1 = OperantAcquisitionPhase(
            agent=self.agent,
            stimuli=self.stimuli,
            n_trials=n_stage_1,
            reward_schedule=schedule_stage_1,
            params=self.params,
        )
        stage_1.name = "shaping_stage_1"

        stage_2 = OperantAcquisitionPhase(
            agent=self.agent,
            stimuli=self.stimuli,
            n_trials=n_stage_2,
            reward_schedule=schedule_stage_2,
            params=self.params,
        )
        stage_2.name = "shaping_stage_2"

        phases = [stage_1, stage_2]
        history = []
        for phase in phases:
            phase.validate(history)
            history.append(phase)

        self.n_trials = n_stage_1 + n_stage_2
        return phases

