# experiment/factories/protocol_factory.py

"""
Protocol factory.

Thin construction layer for multi-phase protocols.
All protocol-specific validation lives in the protocol class itself.

Protocols must read all settings from `params`.
"""

from typing import Any

from protocols.catalog import PROTOCOL_BUILDERS
from virtual_shaping_lab.domain.naming import normalize_protocol_key


PROTOCOL_REGISTRY = dict(PROTOCOL_BUILDERS)


def validate_protocol(name: str) -> None:
    normalized = normalize_protocol_key(name)
    if normalized not in PROTOCOL_REGISTRY:
        available = ", ".join(sorted(PROTOCOL_REGISTRY.keys()))
        raise KeyError(
            f"Unknown protocol '{name}' (normalized='{normalized}'). "
            f"Available protocols: {available}"
        )


def build_protocol(name: str, *, agent: Any, stimuli: Any = None, params: dict[str, Any] | None = None):
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
    normalized = normalize_protocol_key(name)
    validate_protocol(normalized)

    protocol_cls = PROTOCOL_REGISTRY[normalized]

    return protocol_cls(
        agent=agent,
        stimuli=stimuli,
        params=params or {},
    )
