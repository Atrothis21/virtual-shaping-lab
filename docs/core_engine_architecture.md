# Core Engine Architecture (V2.11)

## Purpose
This document describes the current core engine architecture for Virtual Shaping Lab (V2.11), including runtime control flow, object boundaries, extension points, and known gaps.

---

## Top-Level Architecture

The engine is organized into seven layers:

1. Config + Plan Layer
2. Parameter Composition Layer
3. Assembly Layer
4. Runtime Orchestration Layer
5. Behavior Layer (Protocols + Phases)
6. Agent Cognition Layer
7. Runtime Record + Analysis Boundary

The design is contract-first and composition-first:
- runtime units must implement runnable hooks (`reset`, `iter_steps`)
- protocols compose phases
- agent composes representation + learner + policy
- analysis consumes stable records rather than runtime objects

---

## 1) Config + Plan Layer

Primary files:
- `virtual_shaping_lab/experiment/config.py`
- `virtual_shaping_lab/experiment/plan_builder.py`
- `virtual_shaping_lab/experiment/domain/types.py`

Responsibilities:
- parse/normalize payloads into `ExperimentConfig`
- build deterministic `ExperimentPlan` snapshots
- resolve inferred contexts and representation context lists
- provide replay identity with `ExperimentPlan.stable_hash()`

Key contracts:
- `ExperimentPlan.to_dict()/from_dict()/stable_hash()`
- `TrialTimeSpec`, `TrialSchedule`, `StepResult`

Design intent:
- move wiring/inference decisions to planning time
- keep runtime execution deterministic and serializable

---

## 2) Parameter Composition Layer

Primary files:
- `virtual_shaping_lab/experiment/parameters/types.py`
- `virtual_shaping_lab/experiment/parameters/pipeline.py`
- `virtual_shaping_lab/experiment/parameters/composer.py`
- `virtual_shaping_lab/experiment/parameters/ownership_guards.py`

Responsibilities:
- normalize and validate payload-derived parameter drafts
- build typed immutable parameter objects (`ExperimentParameters`)
- provide deterministic serialization (`parameters_to_dict`)
- enforce subsystem ownership boundaries at execution entry points

Key contracts:
- `ParameterNormalizerPipeline`
- `ParameterValidatorPipeline`
- `ParameterComposer.compose(...)`
- `validate_composed_parameter_ownership(...)`

Design intent:
- make execution depend on typed contracts, not free-form payload dicts
- enforce representation/learner/policy/runtime/unit ownership explicitly
- preserve deterministic plan/replay identity

---

## 3) Assembly Layer

Primary files:
- `virtual_shaping_lab/experiment/assemble.py`
- `virtual_shaping_lab/experiment/factories/*`
- `virtual_shaping_lab/protocols/catalog.py`

Responsibilities:
- construct representation, learner, policy, agent
- build runtime units from phase/protocol names
- route to protocol or atomic phase factories
- attach resolved/inferred context labels

Extension points:
- learner/policy/representation/phase/protocol registries
- protocol builder catalog (`PROTOCOL_BUILDERS`)

Design intent:
- keep object creation out of runtime execution
- support open/closed extension via registries/catalogs

---

## 4) Runtime Orchestration Layer

Primary files:
- `virtual_shaping_lab/experiment/runner.py`
- `virtual_shaping_lab/experiment/trial_executor.py`
- `virtual_shaping_lab/experiment/runtime_records.py`
- `virtual_shaping_lab/experiment/sinks.py`
- `virtual_shaping_lab/experiment/hooks.py`

Responsibilities:
- execute runnable units only (`iter_steps` contract)
- manage shared `ExperimentContext` (agent, rng, clock, settings)
- support trial-level and tick-level execution:
  - `update_mode = trial | tick`
  - `record_mode = trial | tick`
- finalize and emit stable records through sinks
- emit lifecycle hooks

Control flow:
1. Runner resets unit
2. Unit yields `StepResult`
3. Runner extracts base record + optional `TrialSchedule`
4. If schedule exists, delegate tick loop to `TrialExecutor`
5. Finalize each emitted record
6. Emit to sink and append to output

Design intent:
- keep runner thin and protocol/phase-agnostic
- isolate intra-trial timing logic in `TrialExecutor`

World schedule runtime contracts consumed by trial execution:
- `virtual_shaping_lab/experiment/world/schedules/*`

---

## 5) Behavior Layer (Protocols + Phases)

Primary files:
- `virtual_shaping_lab/protocols/base.py`
- `virtual_shaping_lab/experiment/phases/base.py`
- `virtual_shaping_lab/experiment/phases/templates/*`
- `virtual_shaping_lab/protocols/*.py`
- `virtual_shaping_lab/experiment/phases/*.py`

Responsibilities:
- Protocols:
  - compose ordered phase sequences for phenomena
  - validate ordering constraints
  - propagate protocol/subphase metadata
- Phases:
  - define trial-level contingencies and sampling
  - define learning-enabled/disabled behavior
  - produce serializable trial records
  - optionally provide trial schedule for tick execution

Design intent:
- protocol handles composition
- phase handles local trial mechanics
- no learning math in protocol classes

V2.11 policy:
- canonical classical phase keys are template-backed only
- no `*_legacy` phase aliases remain in runtime phase construction
- class-based custom/control-flow exceptions remain:
  - `context_shift`
  - `criterion_shift`
- protocol/phase runtime code is factory-quarantined (imports through public seams)

---

## 6) Agent Cognition Layer

Primary files:
- `virtual_shaping_lab/agents/composed_agent.py`
- `virtual_shaping_lab/agents/interfaces.py`
- `virtual_shaping_lab/domain/types.py`
- `virtual_shaping_lab/agents/representations/*`
- `virtual_shaping_lab/agents/learners/*`
- `virtual_shaping_lab/agents/policies/*`

Core contracts:
- `Observation` -> consumed by representation
- `EncodedState` -> consumed by learner/policy
- `Transition` -> consumed by learner update

Composed agent contract:
- `observe(observation) -> EncodedState`
- `act(state, actions, rng) -> action`
- `learn(transition) -> None`
- `value(state, action=None) -> float`

Mechanism ownership split:
- representation-owned:
  - context feature gating/namespacing
  - similarity spreading
  - salience scaling
- learner-owned:
  - attention modulation of update strength

Design intent:
- agent is a thin orchestrator, not a math container
- learners own value state and update equations
- policies are read-only selectors

---

## 7) Runtime Record + Analysis Boundary

Primary files:
- `virtual_shaping_lab/experiment/domain/types.py` (`TrialRecord`)
- `virtual_shaping_lab/analysis/domain/*`
- `virtual_shaping_lab/analysis/views.py`
- `virtual_shaping_lab/analysis/report/catalog.py`
- `virtual_shaping_lab/analysis/registry.py`

Responsibilities:
- runtime emits stable record schema
- analysis converts records into trial/tick views
- protocol-to-report defaults selected via report catalog
- templates are compositional and versioned (`ReportTemplateSpec`)

Current analysis template behavior:
- default mapping by protocol key
- fallback template with explicit warning
- protocol key normalization for catalog lookups

Design intent:
- strict runtime -> analysis boundary
- analysis depends on records, not runtime internals

---

## End-to-End Execution Trace

1. Payload -> `ExperimentConfig`
2. Parameter normalize/validate/compose -> typed `ExperimentParameters` snapshot
3. `ExperimentConfig` -> `ExperimentPlan` (resolved + deterministic)
4. `assemble_experiment(plan)` builds:
   - representation
   - learner
   - policy
   - `ComposedAgent`
   - runtime units (protocols/phases)
5. `Runner.run()` executes units:
   - `iter_steps(ctx)` loop
   - optional tick execution via `TrialExecutor`
6. Records finalized (`TrialRecord` schema) and emitted to sink
7. Analysis reads records and generates metrics/figures/reports

---

## Extension Surfaces

Supported extension seams:
- Add protocol:
  - implement protocol class
  - register in `protocols/catalog.py`
- Add phase:
  - implement `PhaseBase` hooks
  - register in phase factory
- Add learner/policy/representation:
  - implement respective interface
  - register in factory
- Add analysis report template:
  - add protocol mapping/template in analysis report catalog
  - add metrics/figures if needed

Public facade entrypoints (preferred for cross-layer integration):
- experiment:
  - `virtual_shaping_lab/experiment/public.py`
  - `build_plan(...)`, `validate_plan(...)`, `assemble_from_plan(...)`, `run_from_plan(...)`
- analysis:
  - `virtual_shaping_lab/analysis/public.py`
  - `run_preset_report(...)`, `run_default_protocol_report(...)`, `get_protocol_default_template(...)`

Template phase authoring reference:
- `docs/phase_template_authoring.md`

---

## Known Gaps / Risks

### Gap 1: Operant intra-trial semantics are partially trial-index based
Impact:
- FI/VI behavior is not yet fully tick-native across all operant paths.

Recommendation:
- migrate operant reinforcement availability to explicit `TrialSchedule` event semantics for time-critical protocols.

### Gap 2: Assembly still branches by agent type
Impact:
- `assemble.py` has explicit classical vs operant stack branching.

Recommendation:
- converge toward policy-driven assembly only, with `NullPolicy` for classical paths.

### Gap 3: Phase runtime has dual conceptual paths
Impact:
- `PhaseBase.step()` and runnable `iter_steps()` coexist; this increases cognitive overhead.

Recommendation:
- standardize around runnable-first implementation pattern in all phase subclasses.

### Gap 4: Record schema migration tooling is minimal
Impact:
- version field exists, but schema migrations are ad hoc.

Recommendation:
- introduce explicit record-schema migration helpers before v2 schema changes.

### Gap 5: Fallback report template can mask missing mappings
Impact:
- warnings are explicit now, but runtime still succeeds silently from product perspective.

Recommendation:
- add optional strict mode to fail on unmapped protocol templates in CI or debug builds.

### Gap 6: Parameter composition is embedded in plan settings (dict payload)
Impact:
- composed parameters are deterministic but stored as serialized dicts inside settings.

Recommendation:
- promote composed parameter object envelope to a dedicated plan field for stronger typing end-to-end.

---

## Suggested Next Milestones

1. Tick-native operant schedule semantics (FI/VI/VR timing correctness)
2. Unified policy-driven assembly path (remove remaining classical/operant branch split)
3. Promote composed parameter envelope to first-class typed plan field
4. Strict analysis-template mode for CI
5. Record schema migration framework (`v1 -> v2`)
6. Continue reducing factory exposure by moving registry introspection to facade-level APIs
