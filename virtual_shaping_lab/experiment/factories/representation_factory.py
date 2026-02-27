# experiment/factories/representation_factory.py

from typing import Dict, Type

from virtual_shaping_lab.agents.representations.base import RepresentationBase
from virtual_shaping_lab.agents.representations.vector_configural import VectorConfiguralRepresentation
from virtual_shaping_lab.agents.representations.vector_elemental import VectorElementalRepresentation
from virtual_shaping_lab.agents.representations.vector_hybrid import VectorHybridRepresentation


REPRESENTATION_REGISTRY: Dict[str, Type[RepresentationBase]] = {
    "vector_configural": VectorConfiguralRepresentation,
    "vector_elemental": VectorElementalRepresentation,
    "vector_hybrid": VectorHybridRepresentation,
}


def validate_representation(name: str) -> None:
    if name not in REPRESENTATION_REGISTRY:
        available = ", ".join(sorted(REPRESENTATION_REGISTRY.keys()))
        raise KeyError(
            f"Unknown representation '{name}'. "
            f"Available representations: {available}"
        )


def build_representation(name: str, **params):
    """
    Construct a representation instance.

    Params are passed as a single `params` dict.
    """
    validate_representation(name)
    return REPRESENTATION_REGISTRY[name](params=params)



