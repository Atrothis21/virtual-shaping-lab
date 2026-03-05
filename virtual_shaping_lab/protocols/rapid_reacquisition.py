from protocols.base import BaseProtocol
from experiment.phases.public import build_phase
from experiment.phases.context_shift import ContextShiftPhase


class RapidReacquisitionProtocol(BaseProtocol):
    name = "rapid_reacquisition"

    def build_phases(self):
        params = self.params or {}

        stimuli = self.stimuli or {}
        if isinstance(stimuli, dict):
            cs_plus = stimuli.get("cs_plus", [])
        else:
            cs_plus = stimuli

        if not cs_plus:
            cs_plus = params.get("cs_plus", [])

        if not cs_plus:
            raise ValueError("Rapid reacquisition requires at least one CS+ stimulus")

        n_acq = params.get("n_acquisition_trials", 50)
        n_ext = params.get("n_extinction_trials", 50)
        n_reacq = params.get("n_reacquisition_trials", 20)
        alpha = params.get("alpha", 0.2)

        context_a = params.get("context_a", "A")
        context_b = params.get("context_b", "B")

        phases = [
            build_phase(
                "acquisition_template",
                agent=self.agent,
                stimuli={"cs_plus": cs_plus, "cs_minus": []},
                n_trials=n_acq,
                alpha=alpha,
                context=context_a,
            ),
            ContextShiftPhase(
                agent=self.agent,
                context=context_b,
                stimuli=cs_plus,
                n_trials=0,
                params={"context": context_b},
            ),
            build_phase(
                "nonreinforcement_template",
                agent=self.agent,
                stimuli={"cs_plus": cs_plus, "cs_minus": []},
                n_trials=n_ext,
                alpha=alpha,
                context=context_b,
            ),
            ContextShiftPhase(
                agent=self.agent,
                context=context_a,
                stimuli=cs_plus,
                n_trials=0,
                params={"context": context_a},
            ),
            build_phase(
                "acquisition_template",
                agent=self.agent,
                stimuli={"cs_plus": cs_plus, "cs_minus": []},
                n_trials=n_reacq,
                alpha=alpha,
                context=context_a,
            ),
        ]
        phases[0].name = "acquisition"
        phases[2].name = "nonreinforcement"
        phases[4].name = "acquisition"

        self.n_trials = sum(getattr(p, "n_trials", 0) for p in phases)
        return phases
