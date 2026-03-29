"""Prediction error operators for executable learner core."""

from __future__ import annotations

from dataclasses import dataclass

from .base import ErrorOperator


@dataclass(frozen=True)
class RescorlaWagnerErrorOperator(ErrorOperator):
    """Rescorla-Wagner residual: delta = r - V(s)."""

    def __call__(
        self,
        *,
        reward: float,
        prediction: float,
        next_prediction: float | None = None,
        done: bool = False,
    ) -> float:
        _ = next_prediction, done
        return float(reward) - float(prediction)


@dataclass(frozen=True)
class TD0ErrorOperator(ErrorOperator):
    """TD(0) residual: delta = r + gamma*V(s') - V(s)."""

    gamma: float = 0.0

    def __call__(
        self,
        *,
        reward: float,
        prediction: float,
        next_prediction: float | None = None,
        done: bool = False,
    ) -> float:
        bootstrap = 0.0 if bool(done) else float(next_prediction or 0.0)
        return float(reward) + float(self.gamma) * bootstrap - float(prediction)

