Virtual Shaping Lab - Architecture v2 (Composition-First)

Purpose
This document defines the v2 architecture centered on a single composition-based agent orchestrator.

Core Principles
- Composition over inheritance
- Strategy-based learner/policy/representation
- Shared domain contracts across layers
- Vector-first data flow
- Protocol/phase-owned contingencies and action availability

Shared Domain Contracts
- `domain.types.Observation`
  - `stimuli`, `context`, `compound`, optional `t_s`, `dt_s`, `metadata`
- `domain.types.EncodedState`
  - `x` (vector), optional `key`
- `domain.types.Transition`
  - `s`, `r`, optional `a`, optional `s_next`, `done`, optional `t_s`, `dt_s`, `metadata`

Component Interfaces
- `agents.interfaces.IRepresentation`
  - `reset()`
  - `encode(observation) -> EncodedState`
- `agents.interfaces.ILearner`
  - `reset()`
  - `value(state, action=None) -> float`
  - `update(transition) -> None`
- `agents.interfaces.IPolicy`
  - `reset()`
  - `select_action(state, actions, value_fn, rng)`

Agent Model
- Single orchestrator: `agents.composed_agent.ComposedAgent`
- Methods:
  - `reset()`
  - `observe(observation) -> EncodedState`
  - `act(state, actions, rng) -> action | None`
  - `value(state, action=None) -> float`
  - `learn(transition) -> None`
- `NullPolicy` is used for classical flows (`act -> None`).

Execution Flow
Per trial/tick:
1. Phase builds `Observation`
2. `state = agent.observe(observation)`
3. `action = agent.act(state, available_actions, rng)`
4. Phase/protocol computes reward/outcome
5. Phase builds `Transition`
6. `agent.learn(transition)` (if learning enabled)
7. Record output

Boundaries
- Agent does not own:
  - schedule logic
  - contingency semantics
  - trial timing orchestration
  - action-set availability decisions
- Learner owns all value-function parameters and updates.
- Policy is read-only with respect to learner state.

Classical vs Operant
- Both use the same agent class.
- Classical: `policy = NullPolicy()`
- Operant: `policy = EpsilonGreedyPolicy()`, `SoftmaxPolicy()`, etc.
- Distinction is assembly-time component choice, not agent subclassing.

Runner/Protocol Notes
- Runner uses a standardized phase-stepping loop for protocols.
- Phases provide action availability and RNG-driven action selection via `PhaseBase` helpers.

Compatibility Notes
- Config names `classical_agent` and `operant_agent` remain supported as assembly aliases.
- Legacy split-agent class files were removed in v2.

