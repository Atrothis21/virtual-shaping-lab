from protocols.base import BaseProtocol
from experiment.factories.phase_factory import build_phase


class OccasionSettingProtocol(BaseProtocol):
    name = "occasion_setting"

    def build_phases(self):
        params = self.params or {}

        # Expect two stimuli: occasion setter S and target X
        stimuli = self.stimuli or {}
        if isinstance(stimuli, dict):
            s_stim = stimuli.get("occasion_setter", [])
            x_stim = stimuli.get("target", [])
        else:
            s_stim = params.get("occasion_setter", [])
            x_stim = params.get("target", [])

        if not s_stim or not x_stim:
            raise ValueError("Occasion setting requires 'occasion_setter' and 'target' stimuli")

        S = s_stim[0]
        X = x_stim[0]

        n_train = params.get("n_training_trials", 100)
        n_probe = params.get("n_probe_trials", 20)
        alpha = params.get("alpha", 0.2)

        # Training:
        #   S+X -> US
        #   X alone -> no US
        phases = [
            build_phase(
                "acquisition_template",
                agent=self.agent,
                stimuli={"cs_plus": [(S, X)], "cs_minus": []},
                n_trials=n_train,
                alpha=alpha,
            ),
            build_phase(
                "nonreinforcement_template",
                agent=self.agent,
                stimuli={"cs_plus": [X], "cs_minus": []},
                n_trials=n_train,
                alpha=alpha,
            ),
            build_phase(
                "probe_template",
                agent=self.agent,
                stimuli={"cs_plus": [X, (S, X)], "cs_minus": []},
                n_trials=n_probe,
            ),
        ]
        phases[0].name = "acquisition"
        phases[1].name = "nonreinforcement"
        phases[2].name = "probe"

        self.n_trials = sum(getattr(p, "n_trials", 0) for p in phases)
        return phases
