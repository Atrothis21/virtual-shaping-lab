# Revised V3 Planning Principles

## Updated Baseline Assumption (from V2.19.4)

V3 assumes V2.19.4 is already near closeout with these properties in place:

- canonical payload -> config -> plan -> assembly -> runtime -> records boundaries are in place
- deterministic replay is a core invariant
- phase/runtime construction authority is largely catalog-backed
- world schedule ownership is already consolidated under world-layer execution paths
- attention is learner-owned and vectorized, and compatibility shim behavior has been removed from active runtime semantics

So revised V3 is less "remove old V2 debris" and more:

- formalize
- type
- unify
- stabilize

---

## Canonical Glossary Table

Canonical glossary source of truth:

- `docs/v3_glossary.md`

This table must remain fixed through the full V3 cycle and should be updated only in that file.

---

## Mathematical Object Completion (Normative Addendum)

V3 must represent the mathematical object as executable structure, not only architecture.

Required first-class objects:

- `TrialState` typed carrier for per-trial state variables
- `OperatorPipeline` explicit noncommutative composition sequence
- `LearnerSpec` grammar tuple as a typed object
- `validate_learner_spec(...)` mandatory legality enforcement
- phenomenon-to-operator constraint rules enforced at registry/build time

Execution ordering rule (normative):

- operator order is explicit and fixed by pipeline declaration
- default V3 ordering: `Phi -> C -> G -> E -> P -> Policy -> Env -> Err -> A -> Update -> Measure`

Canonical `TrialState` coordinates (normative):

- `s`: raw environmental situation / presented stimuli
- `x`: encoded representation
- `z`: contextual or eligibility or memory-trace state
- `w`: learned parameters
- `a`: attention / associability state
- `u`: chosen action (always present; null/singleton action in classical cases)
- `y`: realized outcome / reinforcement
- `m`: metadata / schedules / counters / phase state

Persistent vs derived rule (normative):

- `TrialState` coordinates above are the persistent carrier
- prediction and error terms are derived stage outputs unless explicitly cached by contract

Operator stage contract rule (normative):

- every `OperatorStage` declares required input fields and produced output fields over `TrialState`
- stage composition must type-check as a valid chain before runtime execution

TD/lookahead rule (normative):

- for TD/actor-critic/action-value learners, `Err` may consume next-state prediction targets derived after `Env`
- this dependency must be explicit in the stage contract metadata

---

## V2-to-V3 Object Mapping

| V2 Object/Surface | V3 Replacement or Continuation | Coexistence Period | Removal Target |
|---|---|---|---|
| `ExperimentConfig` | `ExperimentSpec` + typed nested specs | v3.1.x-v3.3.x | v3.4.0 |
| `ExperimentPlan` | typed semantic plan root (`ExperimentSpec` persisted with stable hash rules) | v3.1.x-v3.6.x | v3.7.0 |
| `plan.settings` flattening adapters | typed field accessors + explicit adapter module | v3.1.x-v3.2.x | v3.3.0 |
| `experiment.phases.*` recipe classes | environment-program compilers + segment builders | v3.2.x-v3.4.x | v3.5.0 |
| current public experiment facade | facade v2 shim over typed plan/runtime facade | v3.1.x-v3.8.x | v3.9.0 |
| current run/report API payload adapters | canonical typed-spec serialization boundary | v3.1.x-v3.6.x | v3.7.0 |

Identity rule (normative):

- in V3, `ExperimentPlan` is a thin wrapper/alias around `ExperimentSpec` identity and is not a separate semantic layer
- there is one semantic plan root; wrappers/facades may exist only for compatibility

Naming rule (normative):

- `*Spec` suffix is reserved for typed declarative configuration objects
- runtime executable instances do not use `*Spec` and use concrete names (for example `EnvironmentProgram`)

---

## Ownership Split (Authoritative)

Canonical ownership source of truth:

- `docs/v3_ownership_split.md`

Boundary invariant (normative) is defined in that document and applies to all slices.

---

## Reconciled Roadmap Execution Order

Canonical roadmap source of truth:

- `docs/v3_roadmap_order.md`

Execution order and cross-slice dependency tables are maintained in that document.

---

## Slice Template (Governance Format)

Every slice must include:

- Owner
- PRD/Spec Artifact
- CI Gates
- Entry Criteria
- Exit Criteria
- Migration Impact

Use this structure for each V3.x section below.

---

## v3.0.x - Documentation Hardening and Canonical Language Freeze

### Goal

Make V3 docs implementation-safe before architectural refactors.

### Deliverables

- normalize V3 docs to UTF-8
- remove mojibake/corrupted symbols
- publish one canonical glossary table
- publish one terms-and-ownership appendix
- publish one roadmap execution order table

### Governance

- Owner: Architecture/Docs
- Artifact: `docs/v3_glossary.md`, `docs/v3_roadmap_order.md`, `docs/v3_ownership_split.md`
- CI Gates:
  - UTF-8 linter passes on `docs/v3_*.md`
  - mojibake grep check returns 0 matches across `docs/v3_*.md`
- Entry Criteria:
  - V2 closeout docs are frozen for this release line
  - glossary source terms approved once by architecture owner
- Exit Criteria:
  - all V3 planning docs pass UTF-8 validation
  - zero mojibake tokens in V3 planning docs
  - glossary table appears once and is referenced by all slices
- Migration Impact:
  - none on runtime behavior
  - doc links may change; must include redirect notes in PR

---

## v3.1.x - Typed Semantic Plan

### Goal

Promote planning from deterministic container to typed semantic contract.

### Target Objects

- `ExperimentSpec`
- `ProgramSpec`
- `AgentSpec`
- `RepresentationSpec`
- `LearnerSpec`
- `PolicySpec`
- `RuntimeSpec`
- `AnalysisSpec`
- `EnvironmentProgramSpec`

Core runtime plan inputs (for coverage metric):

- `ProgramSpec`
- `AgentSpec` (including representation/learner/policy sub-specs)
- `RuntimeSpec`
- `AnalysisSpec`
- `EnvironmentProgramSpec`

Coverage computation rule:

- typed-spec path coverage is computed from the canonical fixture matrix as:
  - `(fixtures whose runtime plan inputs are consumed via typed attributes only) / (total canonical fixtures)`
- fixtures that rely on compatibility adapters are counted as not covered

### Governance

- Owner: Spec/Runtime
- Artifact: typed models + schema tests + migration adapter doc
- CI Gates:
  - plan schema contract tests require all mandatory typed sections
  - stable-hash roundtrip: 10/10 repeated builds under same canonical payload + seed hash-equal
  - deterministic serialization contract: parse(serialize(x)) == x for all core fixtures
  - static scan gate: 0 occurrences of `dict[str, Any]` in core typed spec modules
  - static scan gate: 0 direct `plan.settings[...]` reads in runtime modules
- Entry Criteria:
  - v3.0 glossary and ownership split docs published
  - mapping table approved for `ExperimentConfig`/`ExperimentPlan` transition
- Exit Criteria:
  - typed-spec path coverage >= 95 percent for core runtime plan inputs (measured by fixture matrix)
  - `build_plan()` returns typed sub-specs for program/agent/runtime/analysis
  - serialization roundtrip preserves equality and stable hash
  - schema tests fail for missing required typed sections
  - runtime modules in allowlist pass typed-attribute-only access check (no raw `plan.settings[...]`)
- Migration Impact:
  - coexistence with V2 facades via typed adapters in this slice
  - deprecation warnings added for direct `plan.settings` runtime dependencies

---

## v3.2.x - Compile Phases/Protocols into Environment Programs

### Goal

Treat phases/protocols as environment program generators.

### Deliverables

- `EnvironmentProgram`
- `EnvironmentSegment`
- `TrialSpec`
- `EventSpec`
- compilers for acquisition/extinction/differential/probe/context-shift families

### Governance

- Owner: Program/Environment
- Artifact: segment compiler package + compile fixtures
- CI Gates:
  - deterministic compile-hash tests: each canonical fixture compiles hash-equal for 20 repeated runs
  - compiler coverage requires all canonical phase families above
  - branch guard: no learner update calls inside phase compiler modules
- Entry Criteria:
  - typed `ProgramSpec` and `EnvironmentProgramSpec` available from v3.1
  - canonical fixture inventory frozen for this slice
- Exit Criteria:
  - canonical phases compile to standardized segment output
  - no phase class contains learner math
  - compiled environment program hash is stable under identical input
- Migration Impact:
  - phase recipe APIs remain while internals move to compiler-backed outputs
  - phase internals touching runtime logic must be deprecated with warnings

---

## v3.3.x - First-Class Environment Contract

### Goal

Make environment semantics first-class in runtime stepping.

### Target Objects

- `EnvironmentState`
- `TrialState`
- `Observation`
- `Action`
- `ActionSpace`
- `ObservationSpace`
- `Transition`
- `RewardSignal`
- `TerminationSignal`
- `EpisodeStep`

### Governance

- Owner: Runtime/Environment
- Artifact: `IEnvironment` contract + baseline implementations + `TrialState` model
- CI Gates:
  - shared stepping API tests pass for classical and operant fixture sets
  - deterministic replay gate: identical payload + version + seed + program hash produces hash-identical normalized record streams in 10/10 runs
  - termination contract tests verify terminal flags and horizon behavior per fixture
  - `TrialState` schema gate: required carrier fields (`s,x,z,w,a,u,y,m`) must exist in typed model
  - action-field gate: `u` is always present and null/singleton in classical fixtures
- Entry Criteria:
  - environment-program compilers from v3.2 merged
  - rollout harness capable of environment stepping in test mode
- Exit Criteria:
  - runner executes through environment contract
  - reward/transition/termination semantics are environment-owned
  - deterministic replay holds for payload + version + seed + environment program hash
  - runtime stepping consumes and emits typed `TrialState` objects (not ad hoc dict carriers)
  - `TrialState` persistent/derived boundary is documented and enforced by stage contracts
- Migration Impact:
  - runtime stepping path becomes environment-first
  - direct phase-driven stepping APIs marked deprecated and proxied to environment layer

---

## v3.4.x - Universal Policy and Action-Space Semantics

### Goal

Remove architecture-level classical/operant branching.

### Deliverables

- `NullActionSpace` or `SingletonActionSpace`
- `NullPolicy`
- unified agent assembly path

### Governance

- Owner: Agent/Assembly
- Artifact: unified policy/action-space contracts
- CI Gates:
  - assembly tests for classical and operant through one composition root path
  - branch detector (AST lint rule `no_mode_branching_in_assembly`) blocks explicit classical/operant branching in assembly modules
  - policy contract tests require deterministic action selection under seed for stochastic policies
- Entry Criteria:
  - first-class environment contract (v3.3) merged
  - assembly fixtures updated to typed plan inputs
- Exit Criteria:
  - one assembly path handles both families
  - policy presence is spec-driven, not architecture-branch-driven
- Migration Impact:
  - classical/operant specific assembly helpers moved behind deprecated shims
  - removal target version declared in release notes

### Scoped Rule (explicit)

The "no classical/operant branching" rule is enforced in:

- composition root (`assemble` and equivalent builder paths)
- top-level agent assembly seams

It does not prohibit localized behavior-specific branching inside environment dynamics.

---

## v3.4.5.x - Explicit Operator Pipeline Object

### Goal

Make operator composition order explicit, typed, and test-enforced.

### Deliverables

- `OperatorPipeline`
- `OperatorStage`
- canonical pipeline declaration in runtime assembly
- stage input/output field contracts for each declared operator stage
- TD/lookahead contract for post-`Env` target dependencies used by `Err`

### Governance

- Owner: Runtime/Assembly
- Artifact: pipeline declaration module + stage contracts
- CI Gates:
  - pipeline-order contract test verifies declared stage sequence exactly
  - noncommutativity guard test fails when stage order is mutated in controlled fixtures
  - assembly gate ensures runtime executes through `OperatorPipeline` declaration rather than implicit local call order
  - stage-contract gate: every stage declares required-input and produced-output `TrialState` fields
  - type-chain gate: stage outputs satisfy next-stage required inputs across canonical pipelines
- Entry Criteria:
  - first-class environment contract (v3.3) merged
  - universal policy/action-space semantics (v3.4) merged
- Exit Criteria:
  - operator ordering is represented by a first-class pipeline object
  - assembly/runner execute by pipeline declaration, not implicit sequencing
  - pipeline stage identity is included in artifact metadata
  - declared default pipeline order matches normative runtime order for generic trial semantics
- Migration Impact:
  - runtime sequencing internals shift from implicit function flow to declarative stage execution

---

## v3.5.x - Learner Grammar, Compatibility Validation, Preset Registry

### Goal

Formalize learners as validated operator-slot compositions.

### Grammar

`Learner = <trace, predictor, error, attention, updater, policy>`

### Deliverables

- `learner_specs.py`
- `learner_presets.py`
- `learner_compatibility.py`
- typed `LearnerSpec` grammar object: `LearnerSpec(trace, predictor, error, attention, updater, policy)`
- `validate_learner_spec(spec)` mandatory validator
- operator registries by slot
- machine-readable slot registry manifest
- machine-readable family compatibility table
- hard validation rule catalog (illegal tuple reasons + remediation)

### Governance

- Owner: Learning
- Artifact: grammar validator + preset registry + compatibility matrix
- CI Gates:
  - legality tests: all invalid tuples in catalog fail with named error codes
  - constructor legality gate: illegal `LearnerSpec` tuples cannot be instantiated for runtime assembly
  - preset expansion tests: all named presets expand deterministically and hash-stably
  - family smoke tests: minimum 3 runnable fixtures per supported family in CI
  - compatibility-table parity test: runtime-accepted tuples must match table entries exactly
- Entry Criteria:
  - v3.3/v3.4 environment and policy semantics are finalized
  - current learner artifacts (`operator_learner_conditions.md`, `operational_learner.md`) signed off as source inputs
- Enforcement Location (normative):
  - validation is enforced at spec-build time and again at runtime construction/assembly time
  - runtime must fail fast if a tuple bypasses spec-build validation
- Exit Criteria:
  - invalid tuples fail validation centrally
  - named presets expand to legal tuples deterministically
  - preset identity participates in artifact metadata
  - slot registry and compatibility matrix are emitted in machine-readable form
  - runtime cannot construct learner instances without passing `validate_learner_spec`
- Migration Impact:
  - existing learner alias names supported through registry alias map during coexistence
  - unregistered learner combinations hard-fail after alias window closes

---

## v3.6.x - Rollout Engine and Record Schema Finalization

### Goal

Finalize runtime-analysis contract before richer scientific layering.

### Deliverables

- `RolloutRecord`
- schema versioning rules
- rollout/episode/segment identity fields
- replay harness for environment-based rollouts

### Governance

- Owner: Runtime/Records
- Artifact: record schema + replay harness + schema migration rules
- CI Gates:
  - replay determinism gate for fixed identity inputs (10/10 stable record hashes)
  - schema compatibility tests enforce bump rules for breaking/non-breaking changes
  - report-from-records tests validate zero runtime coupling
- Entry Criteria:
  - environment-first runtime stepping in place (v3.3)
  - typed plan/spec identity fields available (v3.1)
- Exit Criteria:
  - analysis/report consume records only
  - report generation works from saved records alone
  - replay harness validates deterministic output under fixed identity inputs
- Migration Impact:
  - introduces explicit schema version bump process
  - downstream analysis consumers must pin or migrate with schema rules

---

## v3.7.x - Temporal Representation and Episode/Horizon Semantics

### Goal

Make representation-time and execution-time explicit and typed.

### Deliverables

- `TemporalBasisSpec`
- `EpisodeSpec`
- `HorizonSpec`
- `TerminationCondition`

### Governance

- Owner: Representation/Runtime
- Artifact: temporal + episode contracts
- CI Gates:
  - temporal fixture tests: 100 percent of supported temporal bases covered by at least 2 fixtures each
  - episode-boundary tests assert terminal flags and horizon stop reasons
  - deterministic temporal replay checks under fixed seed
- Entry Criteria:
  - rollout schema finalized with episode identifiers (v3.6)
  - representation contract stabilized for temporal hooks
- Exit Criteria:
  - explicit temporal semantics exist in representation and runtime boundaries
  - records include episode identity and terminal flags
- Migration Impact:
  - temporal defaults may shift from implicit to explicit; requires preset update sweep
  - backward compatibility handled via explicit defaulting adapter for one release

---

## v3.8.x - Phenomenon Registry and Minimal Operator Bundles

### Goal

Encode scientific coverage as explicit registry contracts.

### Deliverables

- `phenomenon_registry.py`
- entries include:
  - phase recipe
  - minimal operator bundle
  - required operator set constraints (hard requirements)
  - robust reproduction caveat metadata
  - compatible learner families
  - expected readouts
  - validation fixture link

### Governance

- Owner: Science/Registry
- Artifact: phenomenon registry + fixture matrix + caveat taxonomy
- CI Gates:
  - registry-fixture coverage: 100 percent of canonical registry entries map to a runnable fixture
  - bundle-ablation checks verify minimal bundle necessity claims
  - operator-constraint gate: phenomenon build/run fails if required operator subset is missing
  - caveat policy checks require each entry to be tagged `minimal_expressible` or `robust_reproduction_ready`
- Entry Criteria:
  - learner registry/compatibility tables available (v3.5)
  - rollout schema stable for phenomenon readouts (v3.6)
- Exit Criteria:
  - canonical phenomenon entries are runnable and CI-validated
  - bundle requirements are explicit and auditable
  - each entry explicitly distinguishes minimal principled expressibility from robust reproduction claims
  - phenomenon registry constraints are enforceable (not descriptive only)
- Migration Impact:
  - no direct runtime breakage
  - public scientific docs and acceptance fixtures may be reclassified as caveats are introduced

---

## v3.8.5.x - Layered UI Abstraction and Teaching Surface

### Goal

Make UI behavior-first by default while progressively revealing mechanism and algebra layers.

### UX Principle (normative)

- primary user path is `Phenomenon -> Experiment -> Behavior -> Mechanism -> Operators -> Algebra`
- operators are explanations first, not primary controls

### Modes

- Preset Mode (default): run locked phenomenon recipes with plain-language expectations and graph previews
- Teaching Mode: step-by-step trial walkthrough with operator highlights and behavior-to-operator explanations
- Builder Mode: controlled parameter editing via learner/model choices, not raw operator wiring
- Expert Mode (optional): full pipeline and `TrialState` inspection/debug views

### Deliverables

- preset cards with:
  - plain-English "what happens"
  - expected readout preview
  - linked hidden mechanism/operator metadata
- progressive reveal panels:
  - Layer 1: intuition
  - Layer 2: mechanism chain in plain language
  - Layer 3: operator view
  - Layer 4: full algebra view
- operator pipeline visualization with stage nodes and per-node read/write `TrialState` fields
- graph-to-operator explainability overlays (trial hover includes prediction/outcome/error/update traces)
- preset taxonomy grouped by operator-difference families (for example similarity/context/attention effects)

### Governance

- Owner: UI/UX + Runtime/Teaching
- Artifact: `docs/v3_ui_contract.md` + UI state/view-model contracts + preset metadata schema
- CI Gates:
  - UI contract tests ensure all preset entries include intuition/mechanism/operator/algebra layers
  - interaction tests verify reveal toggles preserve run payload identity (no semantic drift between layers)
  - explainability tests require behavior graphs to resolve to operator-level explanations for canonical presets
  - control-surface guard blocks raw operator-wiring controls in Preset and Builder modes
  - mode contract tests verify Expert-only exposure of full algebra edit/debug affordances
- Entry Criteria:
  - phenomenon registry entries and minimal bundles stabilized (v3.8)
  - learner grammar/compatibility registry stabilized (v3.5)
  - records/readout schema stabilized for graph overlays (v3.6)
- Exit Criteria:
  - users can complete preset runs without seeing operator symbols by default
  - each canonical preset supports progressive reveal through all layers
  - operator pipeline visualization is consistent with runtime `OperatorPipeline` declaration
  - Builder Mode exposes controlled learner/settings selection without raw algebra editing
- Migration Impact:
  - existing UI panels may be reorganized into mode-based navigation
  - preset metadata schema expands to include reveal/explainability contracts
  - no runtime semantic change; this slice governs presentation and teaching surfaces

---

## v3.9.x - Namespace/Package Reshaping and Public API Stabilization

### Goal

Align physical package layout with stabilized semantics.

### Target Layout

- `vsl/spec/`
- `vsl/program/`
- `vsl/environment/`
- `vsl/agent/representation/`
- `vsl/agent/learning/`
- `vsl/agent/policy/`
- `vsl/rollout/`
- `vsl/records/`
- `vsl/analysis/`
- `vsl/registry/`

### Required Migration Contract

For each moved public module, define:

- old import path
- new import path
- deprecation warning window
- removal release

### Release Cadence (explicit)

- namespace alias period: introduce new paths + import aliases, no hard removals
- facade stabilization period: new public facade becomes default, aliases still active with warnings
- hard removal release: alias paths removed per published schedule

### Governance

- Owner: Platform/Infra
- Artifact: migration map + stable public facade + release migration calendar
- CI Gates:
  - deprecated import warnings for all alias paths
  - public facade contract tests: 100 percent pass with snapshot parity against previous release baseline
  - import-audit test ensures no internal modules keep legacy paths post-hard-removal branch
- Entry Criteria:
  - v3.1-v3.8 semantic contracts merged and stable
  - migration map approved with release owners
- Exit Criteria:
  - public imports are stable and documented
  - package ownership aligns with glossary table
  - compatibility shims are either scoped/deprecated or removed per migration policy
- Migration Impact:
  - high migration burden expected; planned as multi-release
  - external integrators must follow published alias/stabilization/removal timeline

---

## Revised V3 Invariants (Testable)

- phases define experimental recipes, not learning math
- environment owns contingencies and transition dynamics
- learners are valid operator compositions
- policy/action-space semantics are universal at composition-root level
- records remain the stable analysis boundary
- deterministic replay is mandatory
- phenomena are recipe + operator bundle + readout contracts with explicit caveat tiering

---

## What Changed from the Original Plan

1. Baseline assumptions are corrected to 2.19.4 reality.
2. Documentation normalization is elevated to a real v3.0.x slice.
3. Execution order is explicitly reconciled.
4. Every slice now includes full governance fields: entry criteria and migration impact included.
5. CI gates are tightened into named assertions and thresholds.
6. Added V2-to-V3 object mapping for migration clarity.
7. Added ownership split table directly in the master plan.
8. Learner grammar and phenomenon registry slices now explicitly absorb validation/preset/caveat artifacts.
9. Namespace migration now includes multi-release cadence.
10. Mathematical-object gaps are now explicit: `TrialState`, `OperatorPipeline`, mandatory learner legality validation, and enforceable phenomenon operator constraints.
11. Mathematical contracts are tightened with canonical `TrialState` coordinates, persistent-vs-derived rules, typed stage I/O contracts, and corrected default pipeline order.
12. Added a dedicated layered UI slice (`v3.8.5.x`) for behavior-first presets, progressive reveal, teaching mode, and controlled builder exposure.

---

## Bottom Line

The revised V3 plan is:

- start from a mostly closed V2.19.4 baseline
- normalize docs and language
- formalize typed semantic contracts
- compile recipes into environment programs
- unify runtime/environment/policy structure
- stabilize rollout records
- deepen temporal and scientific registry coverage
- add layered UI abstraction with progressive operator/algebra reveal
- and then reshape package structure with an explicit multi-release migration contract
