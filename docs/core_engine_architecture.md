# Core Engine Architecture (V2.18.0)

## Purpose
This document describes the current core engine architecture for Virtual Shaping Lab (V2.18.0), including runtime control flow, object boundaries, mathematical-object formalization, extension points, test governance, and known gaps.

UI/browser contract authority:
- `docs/ui_contract_manifest.md`
- UI integration notes in `docs/ui_integration_catalogs_and_debug.md` are guidance layered on top of the manifest.

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
- `virtual_shaping_lab/experiment/phases/catalog_runtime.py`
- `virtual_shaping_lab/experiment/phases/public.py`
- `virtual_shaping_lab/protocols/catalog.py`

Responsibilities:
- construct representation, learner, policy, agent
- build runtime units from phase/protocol names
- route to protocol or atomic phase factories
- attach resolved/inferred context labels

Extension points:
- learner/policy/representation/phase/protocol registries
- protocol builder catalog (`PROTOCOL_BUILDERS`)
- phase runtime catalog (`PHASE_BUILDERS` in `experiment.phases.catalog_runtime`)

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

V2.12 policy:
- canonical classical phase keys are template-backed only
- no `*_legacy` phase aliases remain in runtime phase construction
- class-based custom/control-flow exceptions remain:
  - `context_shift`
  - `criterion_shift`
- authoritative runtime phase construction lives in:
  - `experiment.phases.catalog_runtime`
- protocol/runtime code imports phase construction through:
  - `experiment.phases.public`
- `experiment.factories.phase_factory` is compatibility-only shim (deprecation path)

V2.13 template governance additions:
- `PhaseSpec` is versioned (`spec_version`)
- unsupported template spec versions fail fast at contract boundary
- template mechanics strategy keys are explicit and validated:
  - `trial_sampler_strategy`
  - `schedule_builder_strategy`
  - `learning_gate_strategy`
  - `record_builder_strategy`
- canonical template-backed phase params now enforce ownership leakage guards, not just explicit `*_template` keys

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

Attention mathematical contract (v2.17 target):
- attention state is learner-owned and stateful: `A_t in [0,1]^n`
- learning uses attention-gated feature updates, not representation-time mutation:
  - `Delta theta_t = beta * (A_t odot x_t) * delta_t`
  - equivalent: `Delta theta_t = beta * D(A_t) * x_t * delta_t`
- attention dynamics are part of learner evolution:
  - `A_{t+1} = G(A_t, x_t, r_t, y_hat_t, cuewise_contributions)`
- `cuewise_contributions` means per-feature prediction terms (for linear forms: `{ i -> w_i x_i }`)
- protocol/phase/runtime layers must not mutate attention internals directly; they only provide transitions consumed by learner update.

Vector attention invariants (canonical):
- `A_t` is a cuewise associability vector over active input basis `x_t`.
- attended input is defined as `x'_t = A_t odot x_t` with strict shape equality:
  - `shape(A_t) == shape(x_t)`
- learner updates consume `x'_t`; representation/runtime layers must not pre-apply attention mutation.
- scalar-only attention application is non-canonical and must be treated as compatibility behavior only.

### Attention Conformance Crosswalk (V2.17)

Operator mapping:
- `F = pi o L o R`
- attention lives in `L` only (not `R`, not protocol composition).

Module-to-math role mapping:
- `virtual_shaping_lab/experiment/config.py`
  - enforces attention object contract (`attention_config.name`, `attention_config.params`) and strategy parameter bounds
  - normalizes legacy map form into explicit strategy form
- `virtual_shaping_lab/experiment/parameters/pipeline.py`
  - validates attention strategy names/params at composition boundary
  - fails fast on out-of-domain parameters (`[0,1]` unit interval where required)
- `virtual_shaping_lab/agents/learners/attention_strategies.py`
  - defines `AttentionContext` sufficient statistics (`active_features`, `feature_contributions`, `total_prediction`, `reward`, `prediction_error`)
  - implements `A_{t+1} = G(...)` strategy updates for `none`, `static`, `pearce_hall`, `mackintosh`
  - enforces bounded associability state (`A_t in [0,1]^n`)
- `virtual_shaping_lab/agents/learners/base.py`
  - canonical learner modulation path via `attention_modulated_state(...)`
  - applies `A_t odot x_t` before learner-specific parameter update
  - captures diagnostics (`alpha_by_stimulus`, `mean_alpha`, `prediction_error`, `cuewise_contributions`)
- `virtual_shaping_lab/agents/learners/rescorla_wagner.py`
- `virtual_shaping_lab/agents/learners/td_value.py`
- `virtual_shaping_lab/agents/learners/q_learner.py`
  - consume the canonical modulated state path rather than separate ad hoc attention logic
- `virtual_shaping_lab/experiment/trial_executor.py`
  - emits runtime debug evidence for attention process state (diagnostics only; no attention mutation)
- `virtual_shaping_lab/experiment/runtime_records.py`
  - validates/persists attention debug fields at record boundary
- `virtual_shaping_lab/experiment/assemble.py`
  - resolves configured attention strategy into learner at assembly time (no phase/protocol ownership)

Domain/codomain contract:
- `A_t in [0,1]^n`
- `D(A_t): X -> X`
- learner update path uses `x'_t = A_t odot x_t`, then model-specific `Delta theta_t`
- attention state update consumes `AttentionContext` and returns bounded next state.

Migration notes (legacy/implicit attention path removal):
- representation-level attention fields are forbidden (`representation.params.attention`, `attention_compound`)
- template/phase parameter leakage of attention keys is blocked by ownership guards
- runtime code no longer relies on implicit representation-time attention mutation
- legacy `experiment.attention` map remains compatibility input only and is translated to explicit strategy config
- active attention updates are strategy-driven inside learners; protocols/phases provide data but do not own attention state transitions.

Design intent:
- agent is a thin orchestrator, not a math container
- learners own value state and update equations
- policies are read-only selectors

### Formal Mathematical Object Map (V2.18.0)

The cognition layer now treats the remaining weak-link mechanisms as first-class mathematical objects routed through assembly rather than helper-only local construction.

Representation objects:
- `ContextMap`
  - implementation: `DefaultContextMap`
  - mapping: `C : O x K -> O_c`
- `SimilarityKernel`
  - implementation: `MatrixSimilarityKernel`
  - mapping: `S : X x X -> R`
- `SalienceOperator`
  - implementation: `DiagonalSalienceOperator`
  - mapping: `Sigma : X -> X`
- `TemporalBasis`
  - implementations:
    - `IdentityTemporalBasis`
    - `BinnedTemporalBasis`
    - `TraceTemporalBasis`
  - mapping: `T : Time -> R^d_t`

Learning objects:
- `PredictionErrorRule`
  - implementations:
    - `RescorlaWagnerPredictionError`
    - `TD0PredictionError`
  - mapping: `delta : (X_t, R_t, X_{t+1}, Theta_t) -> R`
- `AttentionMechanism`
  - implementations:
    - `none`
    - `static`
    - `pearce_hall`
    - `mackintosh`
  - mapping:
    - current state/readout: `A_t : Features -> [0,1]`
    - state update: `A_{t+1} = G(A_t, x_t, r_t, y_hat_t, cuewise_stats)`

Control objects:
- `Policy`
  - implementations:
    - `NullPolicy`
    - `FixedPolicy`
    - `EpsilonGreedyPolicy`
    - `SoftmaxPolicy`
  - mapping: `pi(a | x, theta) in Delta(A)`

### Composition Graph

The current composition graph is:

1. `observation`
2. `ContextMap`
3. `SimilarityKernel`
4. `SalienceOperator`
5. optional `TemporalBasis` augmentation
6. `EncodedState`
7. `PredictionErrorRule` + `AttentionMechanism` inside learner update path
8. `Policy` as decision kernel over actions

Operationally:
- `R(observation) -> EncodedState`
- `L(transition, state) -> updated learner parameters`
- `pi(state, actions) -> action or distribution`

### Ownership Boundaries

Representation-owned:
- context normalization/gating
- similarity spreading
- salience scaling
- temporal basis expansion

Learner-owned:
- prediction-error computation
- attention state/update
- value parameters and update rules

Policy-owned:
- action selection
- optional action-distribution inspection

Runtime-owned:
- RNG
- execution order
- trial/tick scheduling
- record emission

Protocols/phases-owned:
- behavioral program structure
- local contingencies
- availability/reward schedules
- phase/protocol ordering

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
  - register in `experiment.phases.catalog_runtime`
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

## Test + CI Governance (V2.18.0)

CI truth is now architecture-first and ordered by risk:
1. guard bucket (`tests/v2_11_guards`)
2. contract bucket (`tests/v2_11_contract`)
3. behavioral bucket (`tests/behavioral_signatures`)
4. selected unit slices (`tests/test_run_api_contract.py`, `tests/test_api_contract_snapshots.py`, `tests/test_visualizations.py`)

Math-object closeout gates added in V2.18.0:
- `tests/test_math_object_interfaces.py`
- `tests/test_math_object_contracts.py`
- direct ownership/config gates for nested learner math objects

Transitional compare mode:
- full-suite run is retained as a temporary non-blocking compare job (`full_suite_compare`) for parity monitoring during migration.

Warning policy:
- architecture-critical buckets run with `-W error`
- only explicitly allowlisted transitional warnings are permitted
- allowlist is documented in `.github/warning_allowlist_architecture.md` with owner/review date/removal trigger

Retirement policy:
- legacy-only/duplicate tests are removed only after replacement mapping is explicit in `V2.14_test_ownership_matrix.md` and bucket gates remain green.

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

### Gap 7: Deprecated phase-factory shim remains for compatibility
Impact:
- `experiment.factories.phase_factory` still exists to preserve backwards compatibility for legacy import paths.

Recommendation:
- remove the shim in the next hard-cut cycle after import migration window closes.

### Gap 8: Extension metadata is descriptive rather than fully runtime-bound
Impact:
- extension/catalog surfaces expose math-object family metadata, but not run-specific instantiated object identity.

Recommendation:
- attach instantiated mechanism provenance to run artifacts as part of closeout/runtime reproducibility work.

---

## Suggested Next Milestones

1. Tick-native operant schedule semantics (FI/VI/VR timing correctness)
2. Unified policy-driven assembly path (remove remaining classical/operant branch split)
3. Promote composed parameter envelope to first-class typed plan field
4. Strict analysis-template mode for CI
5. Record schema migration framework (`v1 -> v2`)
6. Continue reducing factory exposure by moving registry introspection to facade-level APIs
