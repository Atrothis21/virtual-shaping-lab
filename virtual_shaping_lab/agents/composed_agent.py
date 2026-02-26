# agents/composed_agent.py

from __future__ import annotations

from typing import Any, Optional, Sequence

import numpy as np

from virtual_shaping_lab.agents.interfaces import ILearner, IPolicy, IRepresentation
from virtual_shaping_lab.agents.policies.null_policy import NullPolicy
from virtual_shaping_lab.domain.types import EncodedState, Observation, Transition


class ComposedAgent:
    """Thin composition-based orchestrator for representation, learner, and policy."""

    def __init__(
        self,
        learner: ILearner,
        representation: IRepresentation,
        policy: Optional[IPolicy] = None,
    ):
        self.learner = learner
        self.representation = representation
        self.policy = policy or NullPolicy()
        self._state: Optional[EncodedState] = None

    @staticmethod
    def _ensure_state(state: Any) -> EncodedState:
        if isinstance(state, EncodedState):
            return state
        if isinstance(state, np.ndarray):
            return EncodedState(x=state)
        return EncodedState(x=np.asarray(state, dtype=float))

    def reset(self) -> None:
        self._state = None
        if hasattr(self.representation, "reset"):
            self.representation.reset()
        if hasattr(self.learner, "reset"):
            self.learner.reset()
        if hasattr(self.policy, "reset"):
            self.policy.reset()

    def observe(self, observation: Observation) -> EncodedState:
        encoded = self.representation.encode(observation)
        self._state = self._ensure_state(encoded)
        return self._state

    def act(
        self,
        state: EncodedState,
        actions: Optional[Sequence[Any]] = None,
        rng: Optional[np.random.Generator] = None,
    ) -> Any:
        encoded = self._ensure_state(state)
        pool = list(actions) if actions is not None else []
        generator = rng if rng is not None else np.random.default_rng()
        return self.policy.select_action(encoded, pool, self.value, generator)

    def value(self, state: EncodedState, action: Any = None) -> float:
        encoded = self._ensure_state(state)
        return float(self.learner.value(encoded, action=action))

    def learn(self, transition: Transition) -> None:
        self.learner.update(transition)
