# V2.17 Summary - Attention Object Alignment

## Overview
V2.17 aligns attention with the canonical mathematical structure as a learner-owned, stateful associability object inside `L` in:

`F = pi o L o R`

Primary outcomes:
- attention is treated as an explicit stateful vector object `A_t in [0,1]^n`
- canonical learner modulation path is enforced (`A_t odot x_t`, equivalent to `D(A_t) x_t`)
- strategy contract and sufficient-statistics context are explicit and validated
- attention diagnostics are persisted for interpretation and testability
- model-specific behavioral signatures are verified for Pearce-Hall and Mackintosh families
- architecture docs now include a module-to-math conformance crosswalk and migration notes

---

## Object Contract Changes

### Canonical Object and Equations
- Attention is formalized as a learner-owned process:
  - `A_t in [0,1]^n`
  - `A_{t+1} = G(A_t, x_t, r_t, y_hat_t, cuewise_contributions)`
- Canonical modulation equation is documented and enforced:
  - `Delta theta_t = beta * (A_t odot x_t) * delta_t`
  - equivalent diagonal-operator form: `Delta theta_t = beta * D(A_t) * x_t * delta_t`

### Config and Validation Contract
- `experiment.attention_config` now carries explicit strategy configuration:
  - `name`
  - `params`
- strategy names are constrained (`none`, `static`, `pearce_hall`, `mackintosh`)
- parameter keys and bounds are validated per strategy with deterministic failures
- legacy attention map input is preserved only as compatibility translation to explicit strategy config

### Vectorization Closeout (V2.17.1)
- learner base attention path now applies explicit vector modulation (`x'_t = A_t odot x_t`)
- shape mismatch now fails fast with deterministic error:
  - `attention vector shape mismatch: expected={n}, actual={m}`
- legacy scalar cue-label attention path remains compatibility-only:
  - scalar is expanded to uniform vector when cue basis is not aligned to state basis
  - one-time `DeprecationWarning` is emitted per learner instance
- RW / TD / Q learners now share canonical contribution construction via base helper path, eliminating per-learner duplicated fallback logic

---

## Strategy Contracts and Context Requirements

### Strategy Boundary
Implemented strategy surface:
- `current_alpha(active_features) -> A_t`
- `current_alpha_for_cues(cue_labels)`
- `update_state(context) -> A_{t+1}`

### Required Sufficient Statistics
`AttentionContext` contract includes:
- `active_features`
- `feature_contributions`
- `total_prediction`
- `reward`
- `prediction_error`

Implemented strategies:
- `none` (identity baseline)
- `static` (fixed per-cue overrides)
- `pearce_hall` (surprise-driven updates)
- `mackintosh` (relative cue predictiveness updates)

---

## Diagnostics Fields and Runtime Evidence

Attention diagnostics are exposed and validated through runtime records/debug telemetry:
- `alpha_by_stimulus`
- `mean_alpha`
- `prediction_error`
- `cuewise_contributions`

These fields support trial-level interpretability and conformance checks for strategy behavior.

---

## Behavioral Evidence

### Object-Level Conformance
Added/maintained tests for:
- `[0,1]` bounds
- vector shape consistency
- diagonal modulation behavior (`D(A_t): X -> X`)
- canonical modulation path usage
- strategy resolution/validation failures

### Model-Specific Behavioral Signatures
Added directional (non-brittle) signature tests split by model family:
- Pearce-Hall focused:
  - Hall-Pearce-style negative transfer
  - surprise/reversal extinction dynamics vs static baseline
- Mackintosh focused:
  - learned predictiveness separation
  - learned irrelevance profile weakening vs predictive profile
- Shared/regression:
  - low-attention latent-inhibition-style slowing
  - baseline comparison signatures

---

## Documentation Conformance Mapping

Updated:
- `docs/core_engine_architecture.md`

Added V2.17 attention conformance crosswalk:
- explicit module -> mathematical-role mapping
- explicit `F = pi o L o R` placement for attention in `L`
- explicit domain/codomain mapping for `A_t` and `D(A_t): X -> X`
- migration notes for removed/quarantined implicit attention pathways

---

## Validation

Targeted V2.17 attention/object gate:
- `python -m pytest -q tests/test_config.py tests/test_parameter_validator.py tests/test_attention_strategy_contract.py tests/test_attention_object_conformance.py tests/test_attention_preset_payload_contract.py tests/test_behavioral_attention_model_signatures.py tests/test_behavioral_attention_variants.py tests/test_learners.py tests/test_runtime_records.py tests/test_trial_executor.py tests/test_assemble_coverage.py`

Full regression:
- `python -m pytest -q`

Notes:
- During closeout, full regression exposed pre-existing UI teaching-contract drift in preset HTML pages.
- Fixed by adding required teaching/focus/handoff script includes across preset pages.
- Re-ran UI teaching-contract gate and full regression; both passed.

---

## Net State After V2.17

- attention is a first-class learner-owned mathematical object, not an implicit representation/protocol concern
- canonical modulation path is singular and test-protected
- strategy APIs and context contracts are explicit and enforced
- diagnostics provide auditable evidence for attention dynamics
- model-specific behavioral signatures are reproducible and separated by theory family
- architecture documentation now traces implementation directly to mathematical specification
