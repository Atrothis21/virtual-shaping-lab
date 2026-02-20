# protocols/conditioned_inhibition.py

from typing import Any, Dict, List

from protocols.base import BaseProtocol
from experiment.phases.acquisition import AcquisitionPhase
from experiment.phases.compound_nonreinforcement import CompoundNonReinforcementPhase
from experiment.phases.probe import ProbePhase


class ConditionedInhibitionProtocol(BaseProtocol):
    """
    Conditioned inhibition protocol (standard).

    Recipe:
        1. Acquisition:              A  -> US
        2. Compound nonreinforcement AX -> no US
        3. Summation test:           B vs BX (no US)
        4. Retardation:              X -> US (optional; alias acquisition)

    All parameters are read from params.
    """

    name = "conditioned_inhibition"

    def __init__(
        self,
        agent,
        stimuli: Dict[str, List[Any]] | None = None,
        params: Dict[str, Any] | None = None,
        **_
    ):
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
        def _normalize(stimuli):
            if isinstance(stimuli, dict):
                if "cs_plus" in stimuli and isinstance(stimuli["cs_plus"], list):
                    return stimuli["cs_plus"]
                flat = []
                for v in stimuli.values():
                    if isinstance(v, list):
                        flat.extend(v)
                return flat
            return stimuli

        def _pick_novel_stimulus(pool, used):
            for stim in pool:
                if stim not in used:
                    return stim
            return None

        stimuli = self.stimuli or {}
        excitor_stimuli = _normalize(stimuli.get("cs_plus", []))
        inhibitor_stimuli = _normalize(stimuli.get("cs_minus", []))

        if not excitor_stimuli or not inhibitor_stimuli:
            raise ValueError("conditioned_inhibition requires cs_plus and cs_minus stimuli lists.")

        n_acq = self.params.get("n_acquisition_trials", 50)
        n_inhib = self.params.get("n_inhibition_trials", 50)
        n_retard = self.params.get("n_retardation_trials")
        acquisition_outcome = self.params.get("acquisition_outcome", 1.0)

        # Auto-select novel excitor B
        stimulus_pool = self.params.get(
            "stimulus_pool",
            ["tone", "noise", "light", "click", "lever"]
        )
        used = set(excitor_stimuli) | set(inhibitor_stimuli)
        summation_excitor = _pick_novel_stimulus(stimulus_pool, used)

        if summation_excitor is None:
            raise ValueError(
                "No unused stimulus available for summation test. "
                "Provide params['stimulus_pool'] with extra stimuli."
            )

        n_summation_acquisition_trials = self.params.get(
            "n_summation_acquisition_trials",
            n_acq
        )

        summation_probe_count = 1 + len(inhibitor_stimuli)

        acq_params = dict(self.params)
        acq_params["outcome"] = acquisition_outcome

        phases = [
            AcquisitionPhase(
                agent=self.agent,
                stimuli={"cs_plus": list(excitor_stimuli), "cs_minus": []},
                n_trials=n_acq,
                params=acq_params,
            ),
            AcquisitionPhase(
                agent=self.agent,
                stimuli={"cs_plus": [summation_excitor], "cs_minus": []},
                n_trials=n_summation_acquisition_trials,
                params=acq_params,
            ),
            CompoundNonReinforcementPhase(
                agent=self.agent,
                stimuli={"compound": [excitor_stimuli[0], inhibitor_stimuli[0]]},
                n_trials=n_inhib,
                params=self.params,
            ),
            ProbePhase(
                agent=self.agent,
                stimuli={
                    "cs_plus": [
                        summation_excitor,
                        *(
                            (summation_excitor, x)
                            for x in inhibitor_stimuli
                        )
                    ],
                    "cs_minus": []
                },
                n_trials=summation_probe_count,
                params={**self.params, "deliver_reward": False},
            ),
        ]

        phases[1].name = "summation_acquisition"
        phases[3].name = "summation_probe"

        # Retardation (optional)
        if n_retard is not None:
            retardation = AcquisitionPhase(
                agent=self.agent,
                stimuli={"cs_plus": list(inhibitor_stimuli), "cs_minus": []},
                n_trials=n_retard,
                params=acq_params,
            )
            retardation.name = "retardation"
            phases.append(retardation)

        # Validate phase ordering
        history = []
        for phase in phases:
            phase.validate(history)
            history.append(phase)

        self.n_trials = sum(getattr(p, "n_trials", 0) for p in phases)
        return phases
