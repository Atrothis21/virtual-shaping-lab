# protocols/extinction.py

from typing import Any, Dict, List, Optional

from protocols.base import BaseProtocol
from experiment.phases.acquisition import AcquisitionPhase
from experiment.phases.nonreinforcement import NonReinforcementPhase


class ExtinctionProtocol(BaseProtocol):
    """
    Extinction protocol composed of two phases:
        1. Acquisition
        2. Non-reinforcement (extinction)

    All parameters are read from params.
    """

    name = "extinction"

    def __init__(
        self,
        agent,
        stimuli: Dict[str, List[Any]] | None = None,
        params: Optional[Dict[str, Any]] = None,
        **_
    ):
        # Enforce dict-only stimuli
        if stimuli is not None and not isinstance(stimuli, dict):
            raise ValueError("ExtinctionProtocol expects stimuli as a dict with cs_plus/cs_minus.")

        self.agent = agent
        self.stimuli = stimuli or {}
        self.params = params or {}

        super().__init__(
            agent=agent,
            stimuli=self.stimuli,
            n_trials=0,
            params=self.params,
        )

    def build_phases(self):
        stimuli = self.stimuli
        if "cs_plus" not in stimuli or not isinstance(stimuli["cs_plus"], list) or not stimuli["cs_plus"]:
            raise ValueError("ExtinctionProtocol requires stimuli['cs_plus'] to be a non-empty list.")

        n_acq = self.params.get("n_acquisition_trials", 50)
        n_ext = self.params.get("n_extinction_trials", 50)
        acquisition_outcome = self.params.get("acquisition_outcome", 1.0)

        acq_params = dict(self.params)
        acq_params["outcome"] = acquisition_outcome
        acquisition = AcquisitionPhase(
            agent=self.agent,
            stimuli=stimuli,
            n_trials=n_acq,
            params=acq_params,
        )

        extinction = NonReinforcementPhase(
            agent=self.agent,
            stimuli=stimuli,
            n_trials=n_ext,
            params=self.params,
        )

        phases = [acquisition, extinction]

        # Validate phase ordering
        history = []
        for phase in phases:
            phase.validate(history)
            history.append(phase)

        self.n_trials = sum(getattr(p, "n_trials", 0) for p in phases)
        return phases
