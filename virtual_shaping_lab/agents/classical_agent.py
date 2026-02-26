# agents/classical_agent.py

from __future__ import annotations

from typing import Optional

from virtual_shaping_lab.agents.composed_agent import ComposedAgent
from virtual_shaping_lab.agents.policies.null_policy import NullPolicy
from virtual_shaping_lab.domain.types import EncodedState, Observation


class ClassicalAgent(ComposedAgent):
    """Compatibility wrapper over ComposedAgent for classical workflows."""

    def __init__(self, learner, representation):
        super().__init__(learner=learner, representation=representation, policy=NullPolicy())

    def act(self, state: EncodedState, actions=None, rng=None):
        return None
