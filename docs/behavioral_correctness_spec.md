# Behavioral Correctness Specification (V2.18.1)

## Purpose
This document defines the behavioral acceptance contract for V2.18.1.

It is narrower than a full scientific theory statement and broader than a type/interface contract.
Its purpose is to answer:

- what qualitative behaviors must remain true for V2 to be considered scientifically stable
- what tolerances are currently accepted for canonical fixtures
- which null/default semantics are locked
- which interaction assumptions are part of acceptance
- what remains intentionally out of scope

This document is the review-layer companion to:

- `docs/behavioral_invariants_v2_18_1.md`
- `tests/golden_behavior_fixtures.py`
- `tests/behavioral_signatures/*`

The keywords `must`, `must not`, and `may` are normative.

---

## Acceptance Model

V2.18.1 behavioral acceptance requires all of the following:

1. Mechanism-level invariants hold.
2. Canonical behavioral fixtures remain green.
3. Null/default reductions remain behaviorally equivalent to their baselines.
4. Cross-mechanism interaction regressions remain green.
5. Run artifacts expose enough provenance to explain which mechanism stack produced the result.

Behavioral acceptance is therefore based on:

- direct mechanism contracts
- canonical end-to-end signatures
- locked baseline equivalences
- interaction and layer-separation regressions

No single test class is sufficient by itself.

---

## Canonical Fixture Set

The following fixtures define the minimum V2 behavioral surface:

### 1. Acquisition Rise
Expected qualitative signature:
- late-trial prediction exceeds early-trial prediction

Acceptance threshold:
- `min_prediction_gain >= 0.1`

### 2. Extinction Decline
Expected qualitative signature:
- extinction tail falls below both early-extinction and late-acquisition prediction levels

Acceptance thresholds:
- `min_extinction_drop_vs_early >= 0.2`
- `min_extinction_drop_vs_acquisition >= 0.2`

### 3. Blocking Present
Expected qualitative signature:
- the pretrained/primary cue remains dominant over the blocked cue signal

Acceptance threshold:
- `min_primary_minus_blocked >= 0.0`

### 4. Overshadowing Salience Sensitivity
Expected qualitative signature:
- the higher-salience cue remains dominant during compound learning

Acceptance threshold:
- `min_dominance_margin >= 0.0`

### 5. Generalization Gradient Decline
Expected qualitative signature:
- responding declines as similarity distance from the reinforced cue increases

Acceptance threshold:
- `min_cs_plus_minus_gap >= 0.2`

### 6. Renewal Recovery Under Context Switch
Expected qualitative signature:
- probe responding recovers above extinction after context change

Acceptance thresholds:
- ABA: `min_probe_recovery >= 0.2`
- ABC: `min_probe_recovery >= 0.1`

### 7. FI vs FR Separation
Expected qualitative signature:
- fixed-ratio schedules yield higher reinforcement density than fixed-interval schedules in the current operant path

Acceptance threshold:
- `min_reinforcement_density_gap >= 0.6`

---

## Interpretation of Fixture Thresholds

These thresholds are acceptance guardrails, not claims of exact scientific calibration.

They must be interpreted as:

- strong enough to reject subtly wrong semantics
- loose enough to tolerate deterministic implementation details and seeded stochasticity
- stable enough to serve as CI guardrails during closeout

Thresholds may be tightened later only if:

- the behavioral rationale is explicit
- the affected fixtures remain scientifically interpretable
- the change is documented in closeout or PR summary materials

---

## Null and Default Semantics

The following baseline reductions are mandatory:

- identity similarity must match the no-similarity baseline
- unit salience must match identity salience behavior
- disabled temporal basis must match no temporal augmentation
- `none` attention must match identity learner modulation
- `NullPolicy` must remain passive and actionless

The following default/no-op cases are locked:

- absent time fields with enabled temporal basis must produce a neutral/default temporal encoding and must not fail
- static/uniform attention with all weights `1.0` must match the no-attention baseline
- actionless/classical paths must not emit actions
- policy inspection must not imply policy execution side effects beyond readout

These reductions are part of behavioral acceptance because scientific interpretation depends on being able to disable a mechanism without changing unrelated semantics.

---

## Interaction Assumptions

The following interaction assumptions are part of V2 acceptance:

### Context x Similarity
- similarity spread must remain local to the active context-gated feature basis
- similarity must not leak activation into inactive contexts

### Salience x Attention
- salience and attention must compose through the canonical learner path without changing feature identity
- learner-side attention must not migrate into representation-time salience handling

### Temporal Basis x Prediction Error
- temporal features may affect value targets and prediction error only through the encoded state presented to the learner
- prediction-error rules must not mutate temporal representation state directly

### Policy x Prediction Error
- policy choice may change experienced rewards and future value trajectories in operant paths
- policy must not directly mutate learner parameters during action selection

---

## Layer Separation Requirements

The following layer boundaries are part of acceptance:

### Representation
- representation changes may change encoded state and downstream value estimates
- representation changes must not directly perform learning updates
- representation changes must not directly emit actions

### Learning
- learning changes may alter value state and prediction trajectories
- learning updates must not be triggered merely by policy inspection or value readout
- learner-owned meaning must remain confined to update/value semantics

### Policy / Performance
- policy may change action choice and therefore experienced contingencies
- policy queries must not directly mutate learner parameters
- policy selection must remain a control/readout step, not a learning step

### Runtime
- runner/trial execution may orchestrate observation, action availability, rewards, and record emission
- runtime must not invent scientific meaning beyond the configured mechanism stack

These boundaries exist so regressions can be localized to the correct subsystem.

---

## Provenance Requirements

Behavioral acceptance also requires run-level provenance visibility.

Run artifacts and status/report metadata must expose the active variants for:

- context map
- similarity kernel
- salience operator
- temporal basis
- prediction-error rule
- attention mechanism
- policy

This provenance is required because a behavioral signature is not scientifically reviewable unless the producing mechanism stack is explicit.

---

## Runtime Determinism

V2 runtime execution must satisfy the following replay guarantee:

- identical canonical payload
- identical version metadata
- identical seed

must reproduce identical:

- record emission order
- prediction-error trajectories
- learner weight-update trajectories
- policy action selection when policy stochasticity is seeded
- schedule outcomes when schedule stochasticity is seeded

Randomness used by runtime execution must therefore remain centralized in the runtime-owned RNG carried by `ExperimentContext`.

This guarantee applies to runtime execution semantics. Broader randomness-governance cleanup outside the runtime-owned path remains part of closeout sequencing beyond the original V2.18.1 behavioral hardening pass.

---

## Out of Scope

The following are explicitly out of scope for V2.18.1 acceptance:

- introduction of new phenomenon families
- exact empirical fitting to external datasets
- first-class environment abstractions
- major API envelope redesign
- RL-first architecture changes deferred to V3
- broad claims about all possible parameterizations beyond the guarded canonical/default regimes

V2.18.1 is a behavioral hardening pass over the existing simulator architecture, not a new scientific framework.

---

## Acceptance Gates

The current acceptance gates are:

- `python -m pytest -q tests/test_math_object_contracts.py`
- `python -m pytest -q tests/behavioral_signatures`
- `python -m pytest -q tests/test_behavioral_phenomena_defaults.py`
- `python -m pytest -q tests/test_agents.py tests/test_learners.py tests/test_representations.py`
- `python -m pytest -q tests/test_run_api_contract.py tests/test_full_payloads.py tests/test_api_contract_snapshots.py`

Behavioral correctness is accepted only when these gates remain green together.

---

## V2 Boundary

This acceptance specification applies to V2 as a virtual behavioral lab simulator first.

V2 does not introduce a first-class environment abstraction.
Protocols and phases remain the executable behavioral program layer in V2.

Environment and transition-system abstractions belong to V3.
