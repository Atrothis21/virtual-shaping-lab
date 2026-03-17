# V2 Mechanism Catalog

## Purpose
This document summarizes the finalized V2 mechanism families in domain/codomain terms.

It complements:
- `docs/core_engine_architecture.md`
- `docs/behavioral_invariants_v2_18_1.md`
- `docs/behavioral_correctness_spec.md`

Its goal is to make the V2 mechanism stack explainable without reading source code.

---

## Cognitive Structure

The finalized V2 cognitive composition is:

`observation -> representation -> learner -> policy -> action`

Or, in compact form:

`F = pi o L o R`

Where:
- `R` = representation
- `L` = learner
- `pi` = policy

---

## Representation Mechanisms

### ContextMap

Role:
- normalize observations into an explicit context-labeled form

Domain:
- `Observation x Context`

Codomain:
- context-normalized `Observation`

Current implementation family:
- `DefaultContextMap`

Behavioral responsibility:
- preserve stimulus content
- make context explicit
- remain deterministic

### SimilarityKernel

Role:
- encode generalization/transfer between represented cues or features

Domain:
- `Feature x Feature`

Codomain:
- scalar similarity value in `[0, 1]`

Current implementation family:
- `MatrixSimilarityKernel`

Behavioral responsibility:
- identity self-similarity
- bounded transfer
- no negative transfer weights

### SalienceOperator

Role:
- scale represented feature magnitudes without changing feature identity

Domain:
- encoded feature vector `x in R^n`

Codomain:
- encoded feature vector `x' in R^n`

Current implementation family:
- `DiagonalSalienceOperator`

Behavioral responsibility:
- preserve dimensionality
- preserve feature indexing
- alter magnitude only

### TemporalBasis

Role:
- append time-sensitive basis features to a fixed representation block

Domain:
- runtime time metadata

Codomain:
- temporal feature vector in `R^d_t`

Current implementation families:
- `IdentityTemporalBasis`
- `BinnedTemporalBasis`
- `TraceTemporalBasis`

Behavioral responsibility:
- fixed dimensionality under a fixed config
- deterministic encoding
- neutral/default behavior when timing fields are absent

---

## Learner Mechanisms

### PredictionErrorRule

Role:
- compute scalar residuals used by learner updates

Domain:
- current state, reward, optional next state, learner parameters

Codomain:
- scalar prediction error `delta in R`

Current implementation families:
- `RescorlaWagnerPredictionError`
- `TD0PredictionError`

Behavioral responsibility:
- deterministic residuals
- zero residual when target equals prediction
- no direct parameter mutation

### AttentionMechanism

Role:
- modulate learner-side associability/update strength

Domain:
- learner update context including active features, prediction error, reward, and cuewise contributions

Codomain:
- bounded attention state/readout over active feature domain

Current implementation families:
- `none`
- `static`
- `pearce_hall`
- `mackintosh`

Behavioral responsibility:
- bounded attention in `[0, 1]`
- learner-owned modulation
- deterministic updates under fixed state/input

### Learner Families

Role:
- own value state and update dynamics

Current implementation families:
- `RescorlaWagnerLearner`
- `TDValueLearner`
- `QLearner`

Domain:
- encoded state, transition, learner parameters

Codomain:
- updated value state / updated learner parameters

Behavioral responsibility:
- deterministic seeded update behavior
- separation of value readout from update path
- compatibility with attention and prediction-error objects

---

## Policy Mechanisms

### Policy

Role:
- select or parameterize actions from encoded state/value estimates

Domain:
- encoded state, available actions, value function, RNG when stochastic

Codomain:
- selected action
- optional action distribution over available actions

Current implementation families:
- `NullPolicy`
- `FixedPolicy`
- `EpsilonGreedyPolicy`
- `SoftmaxPolicy`

Behavioral responsibility:
- valid action-selection rule
- deterministic seeded behavior
- no learner mutation during action selection

---

## Runtime-Owned Mechanisms

These are not cognitive mechanisms, but they are part of the V2 execution contract.

### Runner / Trial Executor

Role:
- execute runtime units deterministically
- manage seeded stochasticity
- emit finalized records

Domain:
- runtime units, seed, runtime settings

Codomain:
- stable record stream

### Reward Schedule Runtime

Role:
- govern stochastic or deterministic reward availability in operant paths

Domain:
- action availability, runtime RNG, schedule parameters

Codomain:
- schedule outcomes integrated into runtime transitions

Behavioral responsibility:
- seed-governed stochasticity only
- no ad hoc random sources outside runtime-owned RNG

---

## Ownership Summary

| Mechanism Family | Ownership |
|---|---|
| ContextMap | representation |
| SimilarityKernel | representation |
| SalienceOperator | representation |
| TemporalBasis | representation |
| PredictionErrorRule | learner |
| AttentionMechanism | learner |
| Learner algorithm | learner |
| Policy | policy |
| Schedule runtime | runtime/world |

Rules:
- representation transforms observations into encoded state
- learner owns update semantics
- policy owns action-selection semantics
- runtime owns execution order, RNG, and record emission

---

## V2 Boundary

This catalog remains scoped to V2.

V2 does not yet introduce:
- first-class environment objects
- explicit transition-system architecture
- episode/horizon-first RL abstractions

Those are V3 concerns.

In V2, mechanisms are organized to support a virtual behavioral lab simulator first, with RL-aligned internal semantics where they improve clarity and rigor.
