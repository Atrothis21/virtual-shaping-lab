# agents/operant_agent.py

from __future__ import annotations

from virtual_shaping_lab.agents.composed_agent import ComposedAgent


class OperantAgent(ComposedAgent):
    """Compatibility wrapper over ComposedAgent for operant workflows."""

    def __init__(self, learner, representation, policy):
        super().__init__(learner=learner, representation=representation, policy=policy)
