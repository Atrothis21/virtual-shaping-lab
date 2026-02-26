# experiment/factories/agent_factory.py

from __future__ import annotations

from typing import Dict, Callable, Any


def _build_composed_agent(**params: Any):
    from virtual_shaping_lab.agents.composed_agent import ComposedAgent
    from virtual_shaping_lab.agents.policies.null_policy import NullPolicy

    clean = dict(params)
    learner = clean.pop("learner")
    representation = clean.pop("representation")
    policy = clean.pop("policy", None)

    if policy is None:
        policy = NullPolicy()

    return ComposedAgent(
        learner=learner,
        representation=representation,
        policy=policy,
    )


AGENT_REGISTRY: Dict[str, Callable[..., Any]] = {
    "classical_agent": _build_composed_agent,
    "operant_agent": _build_composed_agent,
    "composed_agent": _build_composed_agent,
}


def validate_agent(name: str) -> None:
    if name not in AGENT_REGISTRY:
        available = ", ".join(sorted(AGENT_REGISTRY.keys()))
        raise KeyError(f"Unknown agent '{name}'. Available agents: {available}")


def build_agent(name: str, **params: Any):
    validate_agent(name)
    return AGENT_REGISTRY[name](**params)
