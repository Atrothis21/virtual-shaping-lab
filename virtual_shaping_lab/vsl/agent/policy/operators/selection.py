"""Core executable policy selection operators."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Mapping, Sequence

import numpy as np

from .base import PolicyOperator, PolicyOutput


def _as_tuple(actions: Sequence[Any] | tuple[Any, ...]) -> tuple[Any, ...]:
    return tuple(actions)


def _scores_from_input(policy_input: Mapping[str, Any], available_actions: tuple[Any, ...]) -> dict[Any, float]:
    raw = policy_input.get("action_values") or policy_input.get("action_scores") or {}
    if isinstance(raw, Mapping):
        return {action: float(raw.get(action, 0.0)) for action in available_actions}
    return {action: 0.0 for action in available_actions}


def _argmax_actions(scores: Mapping[Any, float]) -> tuple[Any, ...]:
    if not scores:
        return ()
    max_score = max(scores.values())
    winners = tuple(action for action, score in scores.items() if score == max_score)
    return winners


def _choose_with_tie_break(
    candidates: tuple[Any, ...],
    *,
    tie_break_rule: str,
    rng: np.random.Generator,
) -> Any:
    if not candidates:
        return None
    if tie_break_rule in {"stable_lexicographic", "first"}:
        return sorted(candidates, key=lambda x: repr(x))[0]
    idx = int(rng.integers(0, len(candidates)))
    return candidates[idx]


def _rng_or_default(rng: Any | None) -> np.random.Generator:
    if isinstance(rng, np.random.Generator):
        return rng
    return np.random.default_rng(0)


@dataclass(frozen=True)
class GreedyActionSelectionPolicy(PolicyOperator):
    tie_break_rule: str = "stable_lexicographic"

    def select(
        self,
        *,
        policy_input: Mapping[str, Any],
        available_actions: tuple[Any, ...] = (),
        rng: Any | None = None,
        metadata: Mapping[str, Any] | None = None,
    ) -> PolicyOutput:
        actions = _as_tuple(available_actions)
        scores = _scores_from_input(policy_input, actions)
        winners = _argmax_actions(scores)
        generator = _rng_or_default(rng)
        action = _choose_with_tie_break(winners, tie_break_rule=self.tie_break_rule, rng=generator)
        md = dict(metadata or {})
        md.setdefault("variant", "greedy")
        md.setdefault("tie_break_rule", self.tie_break_rule)
        return PolicyOutput(action=action, action_scores=scores, available_actions=actions, metadata=md)


@dataclass(frozen=True)
class EpsilonGreedyPolicy(PolicyOperator):
    epsilon: float = 0.1
    tie_break_rule: str = "random"

    def select(
        self,
        *,
        policy_input: Mapping[str, Any],
        available_actions: tuple[Any, ...] = (),
        rng: Any | None = None,
        metadata: Mapping[str, Any] | None = None,
    ) -> PolicyOutput:
        actions = _as_tuple(available_actions)
        scores = _scores_from_input(policy_input, actions)
        generator = _rng_or_default(rng)
        if not actions:
            chosen = None
        else:
            explore = float(generator.random()) < float(self.epsilon)
            if explore:
                chosen = actions[int(generator.integers(0, len(actions)))]
            else:
                winners = _argmax_actions(scores)
                chosen = _choose_with_tie_break(winners, tie_break_rule=self.tie_break_rule, rng=generator)
        uniform = (float(self.epsilon) / len(actions)) if actions else 0.0
        probabilities = {action: uniform for action in actions}
        if actions:
            winners = _argmax_actions(scores)
            exploit_mass = 1.0 - float(self.epsilon)
            per_winner = (exploit_mass / len(winners)) if winners else 0.0
            for action in winners:
                probabilities[action] = probabilities[action] + per_winner
        md = dict(metadata or {})
        md.setdefault("variant", "epsilon_greedy")
        md.setdefault("epsilon", float(self.epsilon))
        md.setdefault("tie_break_rule", self.tie_break_rule)
        return PolicyOutput(
            action=chosen,
            action_scores=scores,
            action_probabilities=probabilities,
            available_actions=actions,
            metadata=md,
        )


@dataclass(frozen=True)
class SoftmaxPolicy(PolicyOperator):
    temperature: float = 1.0

    def select(
        self,
        *,
        policy_input: Mapping[str, Any],
        available_actions: tuple[Any, ...] = (),
        rng: Any | None = None,
        metadata: Mapping[str, Any] | None = None,
    ) -> PolicyOutput:
        actions = _as_tuple(available_actions)
        scores = _scores_from_input(policy_input, actions)
        generator = _rng_or_default(rng)
        if not actions:
            chosen = None
            probabilities: dict[Any, float] = {}
        else:
            temp = float(self.temperature)
            raw = np.array([scores[a] / temp for a in actions], dtype=float)
            max_raw = float(np.max(raw))
            exps = np.array([math.exp(v - max_raw) for v in raw], dtype=float)
            denom = float(np.sum(exps))
            probs_arr = (exps / denom) if denom > 0 else np.full_like(exps, 1.0 / len(actions))
            probabilities = {action: float(probs_arr[idx]) for idx, action in enumerate(actions)}
            chosen_idx = int(generator.choice(len(actions), p=probs_arr))
            chosen = actions[chosen_idx]
        md = dict(metadata or {})
        md.setdefault("variant", "softmax")
        md.setdefault("temperature", float(self.temperature))
        return PolicyOutput(
            action=chosen,
            action_scores=scores,
            action_probabilities=probabilities,
            available_actions=actions,
            metadata=md,
        )


@dataclass(frozen=True)
class UniformRandomPolicy(PolicyOperator):
    def select(
        self,
        *,
        policy_input: Mapping[str, Any],
        available_actions: tuple[Any, ...] = (),
        rng: Any | None = None,
        metadata: Mapping[str, Any] | None = None,
    ) -> PolicyOutput:
        _ = policy_input
        actions = _as_tuple(available_actions)
        generator = _rng_or_default(rng)
        chosen = actions[int(generator.integers(0, len(actions)))] if actions else None
        prob = (1.0 / len(actions)) if actions else 0.0
        probabilities = {action: prob for action in actions}
        md = dict(metadata or {})
        md.setdefault("variant", "uniform_random")
        return PolicyOutput(
            action=chosen,
            action_scores={action: 0.0 for action in actions},
            action_probabilities=probabilities,
            available_actions=actions,
            metadata=md,
        )

