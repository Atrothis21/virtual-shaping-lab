# experiment/factories/protocol_factory.py

"""
Protocol factory.

Thin construction layer for multi-phase protocols.
All protocol-specific validation lives in the protocol class itself.

Protocols must read all settings from `params`.
"""

from typing import Dict, Type, Any

from protocols.base import BaseProtocol
from protocols.operant import OperantConditioningProtocol
from protocols.extinction import ExtinctionProtocol
from protocols.conditioned_inhibition import ConditionedInhibitionProtocol
from protocols.aba_renewal import ABARenewalProtocol
from protocols.abc_renewal import ABCRenewalProtocol
from protocols.aab_renewal import AABRenewalProtocol
from protocols.rapid_reacquisition import RapidReacquisitionProtocol
from protocols.occasion_setting import OccasionSettingProtocol
from protocols.blocking import BlockingProtocol
from protocols.matching_law import MatchingLawProtocol


PROTOCOL_REGISTRY: Dict[str, Type[BaseProtocol]] = {
    "operant_conditioning": OperantConditioningProtocol,
    "extinction": ExtinctionProtocol,
    "conditioned_inhibition": ConditionedInhibitionProtocol,
    "aba_renewal": ABARenewalProtocol,
    "abc_renewal": ABCRenewalProtocol,
    "aab_renewal": AABRenewalProtocol,
    "rapid_reacquisition": RapidReacquisitionProtocol,
    "occasion_setting": OccasionSettingProtocol,
    "blocking": BlockingProtocol,
    "matching_law": MatchingLawProtocol,
}


def validate_protocol(name: str) -> None:
    if name not in PROTOCOL_REGISTRY:
        available = ", ".join(sorted(PROTOCOL_REGISTRY.keys()))
        raise KeyError(
            f"Unknown protocol '{name}'. "
            f"Available protocols: {available}"
        )


def build_protocol(name: str, *, agent: Any, stimuli: Any = None, params: Dict[str, Any] = None):
    """
    Construct a protocol instance.

    Required:
      - agent

    Optional:
      - stimuli
      - params (single source of truth for protocol configuration)

    Any protocol-specific validation is the responsibility
    of the protocol class itself.
    """
    validate_protocol(name)

    protocol_cls = PROTOCOL_REGISTRY[name]

    return protocol_cls(
        agent=agent,
        stimuli=stimuli,
        params=params or {},
    )
