# experiment/factories/phase_factory.py

"""
Phase factory.

Thin construction layer for atomic phases.
All phase-specific validation lives in the phase class itself.
"""

from typing import Dict, Type, Any

from experiment.phases.base import PhaseBase
from experiment.phases.acquisition import AcquisitionPhase
from experiment.phases.nonreinforcement import NonReinforcementPhase
from experiment.phases.compound_acquisition import CompoundAcquisitionPhase
from experiment.phases.compound_nonreinforcement import CompoundNonReinforcementPhase
from experiment.phases.differential_acquisition import DifferentialAcquisitionPhase
from experiment.phases.probe import ProbePhase
from experiment.phases.context_shift import ContextShiftPhase


PHASE_REGISTRY: Dict[str, Type[PhaseBase]] = {
    "acquisition": AcquisitionPhase,
    "nonreinforcement": NonReinforcementPhase,
    "compound_acquisition": CompoundAcquisitionPhase,
    "compound_nonreinforcement": CompoundNonReinforcementPhase,
    "differential_acquisition": DifferentialAcquisitionPhase,
    "probe": ProbePhase,
    "context_shift": ContextShiftPhase,
}


def validate_phase(name: str) -> None:
    if name not in PHASE_REGISTRY:
        available = ", ".join(sorted(PHASE_REGISTRY.keys()))
        raise KeyError(
            f"Unknown phase '{name}'. "
            f"Available phases: {available}"
        )


def build_phase(name: str, *, agent: Any, stimuli: Any = None, **phase_params):
    """
    Construct a phase instance.

    Required:
      - agent
      - n_trials (if the phase expects trials)

    All other phase-specific values live in `params`.
    """
    validate_phase(name)
    phase_cls = PHASE_REGISTRY[name]

    # Extract trial count if present; keep the rest in params
    n_trials = phase_params.pop("n_trials", None)
    params = phase_params

    if stimuli is None:
        if n_trials is None:
            return phase_cls(agent=agent, params=params)
        return phase_cls(agent=agent, n_trials=n_trials, params=params)

    if n_trials is None:
        return phase_cls(agent=agent, stimuli=stimuli, params=params)
    return phase_cls(agent=agent, stimuli=stimuli, n_trials=n_trials, params=params)

