from protocols.base import BaseProtocol
from experiment.phases.acquisition import AcquisitionPhase
from experiment.phases.compound_acquisition import CompoundAcquisitionPhase


class BlockingProtocol(BaseProtocol):
    name = "blocking"

    def build_phases(self):
        params = self.params or {}

        stimuli = self.stimuli or {}
        if isinstance(stimuli, dict):
            cs_plus = stimuli.get("cs_plus", [])
            cs_minus = stimuli.get("cs_minus", [])
        else:
            cs_plus = stimuli
            cs_minus = []

        if len(cs_plus) < 2:
            raise ValueError("Blocking requires at least two CS+ stimuli (A and X).")

        A = cs_plus[0]
        X = cs_plus[1]

        n_acq = params.get("n_acquisition_trials", 50)
        n_compound = params.get("n_compound_trials", 50)
        alpha = params.get("alpha", 0.2)

        phases = [
            # Phase 1: A+ acquisition
            AcquisitionPhase(
                agent=self.agent,
                stimuli={"cs_plus": [A], "cs_minus": []},
                n_trials=n_acq,
                params={"n_trials": n_acq, "alpha": alpha},
            ),
            # Phase 2: AX+ compound acquisition
            CompoundAcquisitionPhase(
                agent=self.agent,
                stimuli={"compound": [A, X]},
                n_trials=n_compound,
                params={"n_trials": n_compound, "alpha": alpha},
            ),
        ]

        self.n_trials = sum(getattr(p, "n_trials", 0) for p in phases)
        return phases
