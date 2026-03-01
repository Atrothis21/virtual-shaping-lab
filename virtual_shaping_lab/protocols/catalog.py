"""Protocol builder catalog for runtime assembly."""

from __future__ import annotations

from typing import Any, Callable

from virtual_shaping_lab.domain.naming import normalize_protocol_key

from protocols.aab_renewal import AABRenewalProtocol
from protocols.aba_renewal import ABARenewalProtocol
from protocols.abc_renewal import ABCRenewalProtocol
from protocols.blocking import BlockingProtocol
from protocols.conditioned_inhibition import ConditionedInhibitionProtocol
from protocols.extinction import ExtinctionProtocol
from protocols.matching_law import MatchingLawProtocol
from protocols.occasion_setting import OccasionSettingProtocol
from protocols.operant import OperantConditioningProtocol
from protocols.rapid_reacquisition import RapidReacquisitionProtocol
from protocols.resurgence import ResurgenceProtocol
from protocols.shaping import ShapingProtocol
from protocols.spontaneous_recovery import SpontaneousRecoveryProtocol
from protocols.superextinction import SuperextinctionProtocol


ProtocolBuilder = Callable[..., Any]


PROTOCOL_BUILDERS: dict[str, ProtocolBuilder] = {
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
    "shaping": ShapingProtocol,
    "resurgence": ResurgenceProtocol,
    "superextinction": SuperextinctionProtocol,
    "spontaneous_recovery": SpontaneousRecoveryProtocol,
}


def available_protocols() -> list[str]:
    return sorted(PROTOCOL_BUILDERS.keys())


def validate_protocol_name(name: str) -> None:
    normalized = normalize_protocol_key(name)
    if normalized not in PROTOCOL_BUILDERS:
        available = ", ".join(available_protocols())
        raise KeyError(f"Unknown protocol '{name}' (normalized='{normalized}'). Available protocols: {available}")


def build_protocol(
    name: str,
    *,
    agent: Any,
    stimuli: Any = None,
    params: dict[str, Any] | None = None,
) -> Any:
    normalized = normalize_protocol_key(name)
    validate_protocol_name(normalized)
    protocol_cls = PROTOCOL_BUILDERS[normalized]
    return protocol_cls(agent=agent, stimuli=stimuli, params=params or {})
