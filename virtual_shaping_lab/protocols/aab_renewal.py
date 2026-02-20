from protocols.base import BaseProtocol
from experiment.phases.acquisition import AcquisitionPhase
from experiment.phases.nonreinforcement import NonReinforcementPhase
from experiment.phases.context_shift import ContextShiftPhase
from experiment.phases.probe import ProbePhase


class AABRenewalProtocol(BaseProtocol):
    name = "aab_renewal"

    def build_phases(self):
        params = self.params or {}

        # Prefer stimuli passed via protocol
        stimuli = self.stimuli or {}
        if isinstance(stimuli, dict):
            cs_plus = stimuli.get("cs_plus", [])
        else:
            cs_plus = stimuli

        if not cs_plus:
            cs_plus = params.get("cs_plus", [])

        if not cs_plus:
            raise ValueError("AAB renewal requires at least one CS+ stimulus")

        n_acq = params.get("n_acquisition_trials", 50)
        n_ext = params.get("n_extinction_trials", 50)
        n_probe = params.get("n_probe_trials", 10)
        alpha = params.get("alpha", 0.2)

        context_a = params.get("context_a", "A")
        context_b = params.get("context_b", "B")

        phases = [
            AcquisitionPhase(
                agent=self.agent,
                stimuli={"cs_plus": cs_plus, "cs_minus": []},
                n_trials=n_acq,
                params={"n_trials": n_acq, "alpha": alpha, "context": context_a},
            ),
            NonReinforcementPhase(
                agent=self.agent,
                stimuli={"cs_plus": cs_plus, "cs_minus": []},
                n_trials=n_ext,
                params={"n_trials": n_ext, "alpha": alpha, "context": context_a},
            ),
            ContextShiftPhase(
                agent=self.agent,
                context=context_b,
                stimuli=cs_plus,
                n_trials=0,
                params={"context": context_b},
            ),
            ProbePhase(
                agent=self.agent,
                stimuli={"cs_plus": cs_plus, "cs_minus": []},
                n_trials=n_probe,
                params={"n_trials": n_probe, "context": context_b},
            ),
        ]

        self.n_trials = sum(getattr(p, "n_trials", 0) for p in phases)
        return phases
