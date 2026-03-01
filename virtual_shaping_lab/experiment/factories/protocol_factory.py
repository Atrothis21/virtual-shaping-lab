# experiment/factories/protocol_factory.py

"""
Protocol factory.

Thin construction layer for multi-phase protocols.
All protocol-specific validation lives in the protocol class itself.

Protocols must read all settings from `params`.
"""

from typing import Any

from protocols.catalog import PROTOCOL_BUILDERS


PROTOCOL_REGISTRY = dict(PROTOCOL_BUILDERS)


def validate_protocol(name: str) -> None:
    if name not in PROTOCOL_REGISTRY:
        available = ", ".join(sorted(PROTOCOL_REGISTRY.keys()))
        raise KeyError(
            f"Unknown protocol '{name}'. "
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
    validate_protocol(name)

    protocol_cls = PROTOCOL_REGISTRY[name]

    return protocol_cls(
        agent=agent,
        stimuli=stimuli,
        params=params or {},
    )
