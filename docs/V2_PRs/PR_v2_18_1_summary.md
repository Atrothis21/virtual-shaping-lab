# V2.18.1 Summary - Behavioral Correctness Hardening After Object Formalization

## Overview
V2.18.1 hardens the V2.18.0 mathematical-object architecture with explicit behavioral contracts, canonical fixture thresholds, interaction regressions, mechanism provenance, and an acceptance specification.

Primary outcomes:
- mechanism-level behavioral invariants are now explicit and test-enforced
- canonical behavioral fixtures and tolerance bands are centralized
- composition order and null/default semantics are locked
- degenerate parameter regimes are detectable
- cross-mechanism interaction regressions are covered
- run artifacts now expose resolved mechanism provenance
- behavioral acceptance criteria are documented as an explicit review contract

This turns V2.18.0 from “architecturally objectified” into “behaviorally reviewable and reproducible.”

---

## Behavioral Invariants

Added:
- `docs/behavioral_invariants_v2_18_1.md`

Covered mechanisms:
- `ContextMap`
- `SimilarityKernel`
- `SalienceOperator`
- `TemporalBasis`
- `PredictionErrorRule`
- `AttentionMechanism`
- `Policy`

What is now explicit:
- required deterministic behavior
- null/default reductions
- must/must-not constraints
- cross-mechanism baseline equivalences
- normative representation composition order

Net effect:
- V2 now has a behavioral contract layer above the V2.18.0 type/interface layer

---

## Golden Fixtures and Tolerances

Added/centralized:
- `tests/golden_behavior_fixtures.py`
- `tests/behavioral_signatures/test_golden_fixtures.py`

Canonical fixture set:
- acquisition rise
- extinction decline
- blocking present
- overshadowing salience sensitivity
- generalization gradient decline
- renewal recovery
- FI vs FR separation

What changed:
- qualitative expectations are now declared in one fixture registry
- tolerated acceptance thresholds are centralized instead of repeated across tests
- overlapping default-phenomena tests now consume the shared threshold source

Net effect:
- behavioral acceptance is harder to satisfy accidentally with subtly wrong semantics

---

## Semantics Locking

### Composition Order
The representation mechanism chain is now explicitly locked as:

1. `ContextMap`
2. `SimilarityKernel`
3. encoder projection
4. `SalienceOperator`
5. optional temporal-basis append

Order-sensitive regressions were added so valid-looking reorderings cannot silently change meaning.

### Null / Default Semantics
Locked reductions now include:
- identity similarity == no similarity
- unit salience == identity salience
- disabled temporal basis == no temporal augmentation
- `none` attention == identity learner modulation
- `NullPolicy` == passive/actionless control

Net effect:
- “mechanism absent” and “mechanism neutral” remain scientifically interpretable

---

## Degenerate Regime and Interaction Hardening

### Degenerate Regime Checks
Validator-side `UserWarning` diagnostics now surface dangerous-but-legal configurations such as:
- over-broad similarity kernels
- near-zero salience vectors
- behaviorally inert temporal bases
- frozen attention dynamics
- extreme policy temperatures/epsilons

These remain legal, but they are now CI-visible and auditable.

### Interaction Regressions
Added pairwise interaction coverage for:
- context x similarity
- salience x attention
- temporal basis x prediction error
- policy x prediction error

Net effect:
- interaction regressions are now caught before they can hide inside end-to-end phenomenon drift

---

## Provenance and Layer Separation

### Run-Level Mechanism Provenance
Run/status/report surfaces now expose resolved mechanism provenance for:
- context map
- similarity kernel
- salience operator
- temporal basis
- prediction-error rule
- attention mechanism
- policy

Artifacts now include:
- `mechanism_provenance.json`

### Layer Separation Tests
Added explicit regressions showing:
- policy/readout queries do not imply learning updates
- representation changes do not directly perform learning
- runner control paths do not imply scientific learning semantics when update flow is disabled
- control/value queries remain separable from parameter updates

Net effect:
- regressions can be localized to representation, learning, policy, or runtime more reliably

---

## Acceptance Specification

Added:
- `docs/behavioral_correctness_spec.md`

The spec now defines:
- the V2.18.1 acceptance model
- canonical fixture expectations and thresholds
- null/default semantics
- interaction assumptions
- layer-separation requirements
- provenance requirements
- explicit out-of-scope boundaries
- acceptance gates
- explicit V2 architectural boundary relative to V3

This is the main review document for deciding whether V2 behavior is acceptable, rather than merely well-typed.

---

## Validation

Mechanism/invariant gates exercised during implementation:
- `python -m pytest -q tests/test_math_object_contracts.py`
- `python -m pytest -q tests/test_agents.py tests/test_learners.py tests/test_representations.py`

Golden-fixture / behavioral gates:
- `python -m pytest -q tests/behavioral_signatures`
- `python -m pytest -q tests/behavioral_signatures tests/test_behavioral_phenomena_defaults.py`

Interaction and separation gates:
- `python -m pytest -q tests/test_config.py tests/test_parameter_ownership_guards.py tests/test_math_object_contracts.py`
- `python -m pytest -q tests/test_agents.py tests/test_learners.py tests/behavioral_signatures`
- `python -m pytest -q tests/test_agents.py tests/test_runner_protocol.py tests/test_protocols.py`

Provenance/report gates:
- `python -m pytest -q tests/test_run_api_contract.py tests/test_full_payloads.py tests/test_api_contract_snapshots.py tests/test_report.py`

---

## Net State After V2.18.1

- mechanism objects are not only formalized, but behaviorally constrained
- canonical phenomenon signatures and thresholds are centralized and reusable
- order-sensitive and null/default semantics are now locked
- misleading parameter regimes are surfaced instead of silently accepted
- interaction regressions are covered directly
- run artifacts expose resolved mechanism provenance
- acceptance criteria are now explicit for engineering and scientific review

V2.18.1 therefore closes the largest behavioral ambiguity left after V2.18.0.
