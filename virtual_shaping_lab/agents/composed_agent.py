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
        pool = list(actions) if actions is not None else list(getattr(self.learner, "actions", []))
        generator = rng if rng is not None else np.random.default_rng()
        return self.policy.select_action(encoded, pool, self.value, generator)

    def value(self, state: EncodedState, action: Any = None) -> float:
        encoded = self._ensure_state(state)
        return float(self.learner.value(encoded, action=action))

    def learn(self, transition: Transition) -> None:
        self.learner.update(transition)

    # Backward-compatible entrypoint for current phase code.
    def update(
        self,
        state: EncodedState,
        reward: float,
        action: Any = None,
        next_state: Optional[EncodedState] = None,
        done: bool = False,
        t_s: Optional[float] = None,
        dt_s: Optional[float] = None,
        metadata: Optional[dict[str, Any]] = None,
    ) -> None:
        transition = Transition(
            s=self._ensure_state(state),
            r=float(reward),
            a=action,
            s_next=None if next_state is None else self._ensure_state(next_state),
            done=bool(done),
            t_s=t_s,
            dt_s=dt_s,
            metadata=metadata or {},
        )
        self.learn(transition)

    def update_with_alpha(
        self,
        state: EncodedState,
        reward: float,
        action: Any = None,
        alpha_override: Optional[float] = None,
        delta_override: Optional[float] = None,
        next_state: Optional[EncodedState] = None,
        done: bool = False,
        t_s: Optional[float] = None,
        dt_s: Optional[float] = None,
    ) -> None:
        metadata: dict[str, Any] = {}
        if alpha_override is not None:
            metadata["alpha_override"] = float(alpha_override)
        if delta_override is not None:
            metadata["delta_override"] = float(delta_override)
        self.update(
            state=state,
            reward=reward,
            action=action,
            next_state=next_state,
            done=done,
            t_s=t_s,
            dt_s=dt_s,
            metadata=metadata,
        )
