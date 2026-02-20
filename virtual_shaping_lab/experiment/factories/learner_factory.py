# experiment/factories/learner_factory.py

from typing import Dict, Type

from agents.learners.base import BaseLearner
from agents.learners.rescorla_wagner import RescorlaWagnerLearner
from agents.learners.td_value import TDValueLearner
from agents.learners.q_learner import QLearner


LEARNER_REGISTRY: Dict[str, Type[BaseLearner]] = {
    "rescorla_wagner": RescorlaWagnerLearner,
    "td_value": TDValueLearner,
    "q_learner": QLearner,
}


def validate_learner(name: str) -> None:
    if name not in LEARNER_REGISTRY:
        available = ", ".join(sorted(LEARNER_REGISTRY.keys()))
        raise KeyError(
            f"Unknown learner '{name}'. "
            f"Available learners: {available}"
        )


def build_learner(name: str, **params):
    """
    Construct a learner instance.

    Params are passed through to the learner constructor.
    """
    validate_learner(name)
    return LEARNER_REGISTRY[name](**params)

