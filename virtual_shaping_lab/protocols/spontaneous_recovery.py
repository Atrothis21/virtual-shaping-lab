from typing import Any, Dict, List

from protocols.base import BaseProtocol
from experiment.phases.context_shift import ContextShiftPhase
from experiment.phases.operant_acquisition import OperantAcquisitionPhase
from experiment.world.schedules import build_reward_schedule


class SpontaneousRecoveryProtocol(BaseProtocol):
    """
    Operant spontaneous recovery sequence:
    acquisition in context A -> extinction in context B -> probe in context A.
    """

    name = "spontaneous_recovery"

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
        n_ext = int(self.params.get("n_extinction_trials", 60))
        n_probe = int(self.params.get("n_probe_trials", 30))

        context_a = self.params.get("context_a", "A")
        context_b = self.params.get("context_b", "B")

        acq_schedule = build_reward_schedule(
            self.params.get("acquisition_schedule", {"type": "fixed_ratio", "value": 1, "reward": 1.0})
        )
        extinction_schedule = build_reward_schedule(
            self.params.get("extinction_schedule", {"type": "fixed_ratio", "value": 1, "reward": 0.0})
        )
        probe_schedule = build_reward_schedule(
            self.params.get("probe_schedule", {"type": "fixed_ratio", "value": 1, "reward": 0.0})
        )

        acq = OperantAcquisitionPhase(
            agent=self.agent,
            stimuli=self.stimuli,
            n_trials=n_acq,
            reward_schedule=acq_schedule,
            params={**self.params, "context": context_a},
        )
        acq.name = "spontaneous_recovery_acquisition"

        shift_to_b = ContextShiftPhase(
            agent=self.agent,
            context=context_b,
            stimuli=self.stimuli if isinstance(self.stimuli, list) else self.stimuli.get("cs_plus", ["lever"]),
            params={"context": context_b},
        )

        extinction = OperantAcquisitionPhase(
            agent=self.agent,
            stimuli=self.stimuli,
            n_trials=n_ext,
            reward_schedule=extinction_schedule,
            params={**self.params, "context": context_b},
        )
        extinction.name = "spontaneous_recovery_extinction"

        shift_to_a = ContextShiftPhase(
            agent=self.agent,
            context=context_a,
            stimuli=self.stimuli if isinstance(self.stimuli, list) else self.stimuli.get("cs_plus", ["lever"]),
            params={"context": context_a},
        )

        probe = OperantAcquisitionPhase(
            agent=self.agent,
            stimuli=self.stimuli,
            n_trials=n_probe,
            reward_schedule=probe_schedule,
            params={**self.params, "context": context_a},
        )
        probe.name = "spontaneous_recovery_probe"

        phases = [acq, shift_to_b, extinction, shift_to_a, probe]
        history = []
        for phase in phases:
            phase.validate(history)
            history.append(phase)

        self.n_trials = n_acq + n_ext + n_probe
        return phases

