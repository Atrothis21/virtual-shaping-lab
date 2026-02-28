"""Core experiment runtime types for v2.1 orchestration."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional

import numpy as np

from virtual_shaping_lab.domain.types import Observation


TrialSpec = dict[str, Any]
TrialRecord = dict[str, Any]


@dataclass(frozen=True)
class StepResult:
    """
    Single execution step produced by a runnable unit.

    This is intentionally generic so phases/protocol adapters can adopt it
    incrementally without forcing a tick-based rewrite.
    """

    observation: Observation
    available_actions: list[Any] = field(default_factory=list)
    reward: float = 0.0
    learning_enabled: bool = True
    done: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ExperimentPlan:
    """
    Declarative runtime plan.

    `units` may contain pre-built unit configs or runtime identifiers depending
    on assembly stage.
    """

    units: list[Any]
    seed: Optional[int] = None
    record_schema_version: str = "v1"
    settings: dict[str, Any] = field(default_factory=dict)


@dataclass
class ExperimentContext:
    """Shared mutable runtime context passed across runner and units."""

    agent: Any
    rng: np.random.Generator
    clock_s: float = 0.0
    shared_state: dict[str, Any] = field(default_factory=dict)
    settings: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class RunResult:
    """Execution result envelope for top-level experiment runs."""

    run_id: str
    records: list[TrialRecord] = field(default_factory=list)
    artifacts: dict[str, Any] = field(default_factory=dict)

