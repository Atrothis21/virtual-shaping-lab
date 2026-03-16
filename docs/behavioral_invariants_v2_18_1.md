# Behavioral Invariants (V2.18.1)

## Purpose
This document defines the normative behavioral invariants for the V2.18.1 hardening pass.

These invariants sit on top of the mathematical-object interface contracts from V2.18.0.
They are intended to answer a different question:

- not only "is this mechanism well typed?"
- but also "what behavioral properties must remain true for the mechanism to be scientifically interpretable?"

The keywords `must`, `must not`, and `may` are normative.

---

## 1. ContextMap

### Must
- A context map must preserve the underlying stimulus content of an observation.
- A context map must produce an observation-like value with an explicit context label.
- A context map must be deterministic for identical observation/context inputs.
- A context map must preserve observation timing metadata when present.

### Must Not
- A context map must not invent or remove stimuli.
- A context map must not mutate learner-owned or policy-owned state.
- A context map must not introduce stochasticity in V2.

### Null / Default Semantics
- If context is absent, the default context must be used.
- If no special context behavior is configured, the default mapping is identity on stimuli plus default-context normalization.

---

## 2. SimilarityKernel

### Must
- A similarity kernel must return a scalar value in `[0, 1]`.
- A similarity kernel must return `1.0` for identical feature labels under the default matrix-backed implementation.
- Similarity-induced transfer must be monotone with respect to configured similarity strength:
  higher configured similarity must not produce weaker induced transfer than lower configured similarity, all else equal.
- Spread behavior must include the presented feature set with unit weight.

### Must Not
- A similarity kernel must not produce negative transfer weights.
- A similarity kernel must not create feature labels outside the configured representational domain.
- A similarity kernel must not mutate observations, learner state, or policy state.

### Null / Default Semantics
- With no configured similarity or identity/off-diagonal-zero similarity, behavior must reduce to no cross-feature transfer.
- Identity similarity must be behaviorally equivalent to the no-similarity baseline.

---

## 3. SalienceOperator

### Must
- A salience operator must preserve vector dimensionality.
- A salience operator must scale existing features without changing feature identity.
- For non-negative inputs and non-negative salience weights, output values must remain non-negative.
- Relative salience differences must affect magnitude, not feature indexing.

### Must Not
- A salience operator must not create new non-zero features outside the input support.
- A salience operator must not flip the sign of non-negative inputs under the default non-negative salience regime.
- A salience operator must not reorder features.

### Null / Default Semantics
- Uniform salience of `1.0` must behave as identity scaling.
- Missing salience configuration must reduce to the identity operator or its exact behavioral equivalent.

---

## 4. TemporalBasis

### Must
- A temporal basis must emit a fixed-dimensional vector for a fixed experiment configuration.
- A temporal basis must be deterministic for identical time inputs.
- A temporal basis must preserve dimensionality across runtime steps.
- If enabled, temporal basis dimensionality must be known at learner initialization.

### Must Not
- A temporal basis must not grow or shrink dimensionality during execution.
- A temporal basis must not inject stochasticity in V2.
- A temporal basis must not overwrite the non-temporal representation block.

### Null / Default Semantics
- If temporal basis is disabled, no temporal augmentation must occur.
- If time fields are absent, enabled temporal basis behavior must reduce to the configured neutral/default encoding rather than erroring.

---

## 5. PredictionErrorRule

### Must
- A prediction-error rule must return a scalar residual.
- A prediction-error rule must be deterministic for identical inputs.
- If realized reward equals current prediction target, residual must be zero.
- Zero residual must imply zero parameter update contribution when combined with the canonical learner update rule.

### Must Not
- A prediction-error rule must not mutate learner parameters directly.
- A prediction-error rule must not read representation-owned configuration at update time.
- A prediction-error rule must not depend on UI/runtime/debug metadata for its mathematical value.

### Null / Default Semantics
- Terminal/no-next-state semantics must reduce to the appropriate zero-future-value baseline for TD-style rules.
- Default RW semantics must reduce to `delta = r - y_hat`.

---

## 6. AttentionMechanism

### Must
- Attention state/readout must remain bounded in `[0, 1]`.
- Attention must modulate learning through the learner path, not the representation path.
- Attention updates must be local to the active feature domain or explicitly configured overrides.
- Attention must be deterministic for identical context/state inputs.

### Must Not
- An attention mechanism must not create attention mass for undefined feature labels.
- An attention mechanism must not mutate representation basis or policy state.
- An attention mechanism must not bypass learner-owned update flow.

### Null / Default Semantics
- `none` attention must behave as identity modulation.
- static/uniform attention with all weights `1.0` must be behaviorally equivalent to no attention modulation.
- Missing attention configuration must reduce to the `none` mechanism or its exact behavioral equivalent.

---

## 7. Policy

### Must
- A policy must define a valid action-selection rule over the provided action set.
- If action-distribution inspection is exposed, it must describe the same decision kernel used by `select_action(...)`.
- A stochastic policy distribution must be normalized over available actions.
- Policy behavior must be deterministic under identical seed, state, value function, and action set.

### Must Not
- A policy must not mutate learner parameters during action selection.
- A policy must not fabricate actions outside the provided or configured action domain.
- `NullPolicy` must not emit an action in classical/actionless paths.

### Null / Default Semantics
- `NullPolicy` must be passive and actionless.
- Fixed policy must reduce to a one-hot action distribution over its configured action.
- Missing policy in classical paths must reduce to `NullPolicy`.

---

## Cross-Mechanism Baselines

These baseline reductions must remain true:

- identity similarity == no similarity
- unit salience == identity salience operator
- disabled temporal basis == no temporal augmentation
- `none` attention == identity learner modulation
- `NullPolicy` == no action emission

These baseline equivalences are required so that "feature off" and "mechanism absent" remain scientifically interpretable.

Locked default/no-op cases:
- absent time fields with enabled temporal basis must emit the neutral/default temporal encoding and must not fail
- identity/off-diagonal-zero similarity must match the no-similarity baseline
- uniform/static attention with all weights `1.0` must match the no-attention baseline
- `NullPolicy` must remain passive in both action selection and exposed policy-distribution semantics

---

## Representation Composition Order

The V2 representation chain is order-sensitive and must remain:

1. `ContextMap`
2. `SimilarityKernel`
3. encoder projection into the feature basis
4. `SalienceOperator`
5. optional temporal basis append after the non-temporal representation block

### Must
- Context normalization must occur before similarity spread.
- Similarity spread must be resolved before salience scaling.
- Salience must scale the encoded vector, not the raw observation.
- Temporal basis augmentation must occur after the non-temporal representation vector is formed.

### Must Not
- Salience must not be applied before similarity spread.
- Temporal basis must not be inserted inside the non-temporal feature block.
- Implementations must not silently reorder these mechanisms while preserving interface compatibility.

This order is normative because the mechanisms are not commutative in general.
