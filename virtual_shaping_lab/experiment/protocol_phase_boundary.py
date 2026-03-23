"""Protocol-vs-phase build boundary contract for basis-driven assembly."""

from __future__ import annotations

import hashlib


class ProtocolPhaseBoundaryError(ValueError):
    """Raised when protocol/phase boundary contract is invalid."""


def resolve_unit_build_boundary(
    protocol_name: str,
    *,
    protocol_registry: dict[str, object],
    phase_registry: dict[str, object] | None = None,
    requested_boundary: str | None = None,
) -> str:
    """
    Resolve whether a unit should be assembled as a protocol or atomic phase.

    Boundary semantics:
    - default follows registry membership (`protocol` when registered, else `phase`)
    - `acquisition` remains `phase` by default
    - explicit override via `requested_boundary` is allowed when valid
    """
    key = str(protocol_name or "").strip()
    if not key:
        raise ProtocolPhaseBoundaryError("protocol_name must be a non-empty string.")
    reg = protocol_registry if isinstance(protocol_registry, dict) else {}
    in_registry = key in reg
    phase_reg = phase_registry if isinstance(phase_registry, dict) else {}
    in_phase_registry = key in phase_reg

    requested = None if requested_boundary is None else str(requested_boundary).strip().lower()
    if requested not in {None, "", "phase", "protocol"}:
        raise ProtocolPhaseBoundaryError(
            "requested_boundary must be one of: phase, protocol, or null."
        )

    if requested == "protocol":
        if not in_registry:
            raise ProtocolPhaseBoundaryError(
                f"Protocol boundary requested for '{key}', but no protocol builder is registered."
            )
        return "protocol"
    if requested == "phase":
        if not in_phase_registry:
            raise ProtocolPhaseBoundaryError(
                f"Phase boundary requested for '{key}', but no atomic phase builder is registered."
            )
        return "phase"

    if key == "acquisition":
        return "phase"
    return "protocol" if in_registry else "phase"


def derive_unit_build_key(
    *,
    phase_index: int,
    phase_name: str,
    protocol_name: str,
    build_boundary: str,
    context_id: str | None = None,
) -> str:
    """Derive deterministic unit build key for traceability."""
    index = int(phase_index)
    name = str(phase_name or "").strip() or f"Phase {index}"
    protocol = str(protocol_name or "").strip()
    boundary = str(build_boundary or "").strip().lower()
    context = str(context_id or "-").strip() or "-"
    if boundary not in {"phase", "protocol"}:
        raise ProtocolPhaseBoundaryError("build_boundary must be 'phase' or 'protocol'.")

    identity = f"{index}|{name}|{protocol}|{boundary}|{context}"
    digest = hashlib.sha256(identity.encode("utf-8")).hexdigest()[:10]
    return f"{index:03d}:{boundary}:{protocol}:{context}:{digest}"
