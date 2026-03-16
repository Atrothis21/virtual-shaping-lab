"""Representation package exports.

This package uses lazy exports to avoid import cycles between the
representation-layer math objects and the concrete vector representations.
"""

from __future__ import annotations

from importlib import import_module

__all__ = [
    "RepresentationBase",
    "IdentityRepresentation",
    "VectorElementalRepresentation",
    "VectorConfiguralRepresentation",
    "VectorHybridRepresentation",
]


def __getattr__(name: str):
    if name == "RepresentationBase":
        return getattr(import_module("virtual_shaping_lab.agents.representations.base"), name)
    if name == "IdentityRepresentation":
        return getattr(import_module("virtual_shaping_lab.agents.representations.identity"), name)
    if name == "VectorElementalRepresentation":
        return getattr(import_module("virtual_shaping_lab.agents.representations.vector_elemental"), name)
    if name == "VectorConfiguralRepresentation":
        return getattr(import_module("virtual_shaping_lab.agents.representations.vector_configural"), name)
    if name == "VectorHybridRepresentation":
        return getattr(import_module("virtual_shaping_lab.agents.representations.vector_hybrid"), name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
