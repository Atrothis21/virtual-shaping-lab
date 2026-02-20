# experiment/factories/agent_factory.py

from typing import Dict, Callable, Any


def _build_classical_agent(**params: Any):
    # Flat import — works when project root is on sys.path
    from agents.classical_agent import ClassicalAgent
    clean_params = dict(params)
    clean_params.pop("policy", None)
    return ClassicalAgent(**clean_params)


def _build_operant_agent(**params: Any):
    # Flat import — works when project root is on sys.path
    from agents.operant_agent import OperantAgent
    return OperantAgent(**params)


AGENT_REGISTRY: Dict[str, Callable[..., Any]] = {
    "classical_agent": _build_classical_agent,
    "operant_agent": _build_operant_agent,
}


def validate_agent(name: str) -> None:
    if name not in AGENT_REGISTRY:
        available = ", ".join(sorted(AGENT_REGISTRY.keys()))
        raise KeyError(
            f"Unknown agent '{name}'. "
            f"Available agents: {available}"
        )


def build_agent(name: str, **params: Any):
    """
    Construct an agent instance.

    Params are passed through to the agent constructor.
    """
    validate_agent(name)
    return AGENT_REGISTRY[name](**params)
