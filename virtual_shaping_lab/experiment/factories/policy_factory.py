# experiment/factories/policy_factory.py

from typing import Dict, Callable, Any


def _build_epsilon_greedy(**params: Any):
    from agents.policies.epsilon_greedy import EpsilonGreedyPolicy
    return EpsilonGreedyPolicy(**params)


def _build_softmax(**params: Any):
    from agents.policies.softmax import SoftmaxPolicy
    return SoftmaxPolicy(**params)


def _build_fixed(**params: Any):
    from agents.policies.fixed_policy import FixedPolicy
    return FixedPolicy(**params)


POLICY_REGISTRY: Dict[str, Callable[..., Any]] = {
    "epsilon_greedy": _build_epsilon_greedy,
    "softmax": _build_softmax,
    "fixed": _build_fixed,
}


def validate_policy(name: str) -> None:
    if name not in POLICY_REGISTRY:
        available = ", ".join(sorted(POLICY_REGISTRY.keys()))
        raise KeyError(
            f"Unknown policy '{name}'. "
            f"Available policies: {available}"
        )


def build_policy(name: str, **params: Any):
    """
    Construct a policy instance.

    Params are passed through to the policy constructor.
    """
    validate_policy(name)
    return POLICY_REGISTRY[name](**params)

