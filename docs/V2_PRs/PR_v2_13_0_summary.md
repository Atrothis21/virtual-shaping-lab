# V2.13 Summary - Template Governance and Invariants

## Overview
V2.13 hardens template-phase governance by making template behavior versioned, strategy-validated, and contract-tested.

Primary outcomes:
- introduced `PhaseSpec.spec_version` with strict supported-version validation
- added explicit strategy-key guards for template mechanics composition
- expanded deterministic-run invariants for template-backed plans
- strengthened template record schema/naming contract assertions
- extended ownership leakage guards to canonical template-backed phase keys
- removed known plotting `set_ticklabels(...)` warnings and added warning-regression tests

---

## Delivered Changes

### 1) Template Spec Versioning
Updated:
- `virtual_shaping_lab/experiment/domain/types.py`
- `virtual_shaping_lab/experiment/phases/catalog_runtime.py`

Behavior:
- `PhaseSpec` now includes `spec_version` (default `1`)
- unsupported versions fail fast with explicit error
- canonical template builders propagate explicit spec version

Tests:
- `tests/test_template_spec_versioning.py`

### 2) Strategy-Key Constraints for Template Mechanics
Updated:
- `virtual_shaping_lab/experiment/phases/catalog_runtime.py`

Added validation/resolution for:
- `trial_sampler_strategy`
- `schedule_builder_strategy`
- `learning_gate_strategy`
- `record_builder_strategy`

Behavior:
- unknown strategy keys raise contract-level `ValueError`
- supported strategies resolve to explicit mechanics classes

Tests:
- `tests/test_template_strategy_guards.py`

### 3) Template Determinism Invariants
Added:
- `tests/test_template_determinism.py`

Coverage:
- same plan + seed => identical record stream
- seed changes alter stochastic template sampling behavior where expected

### 4) Record Schema + Naming Invariants
Updated:
- `tests/v2_11_contract/test_template_record_semantics.py`

Coverage:
- required record-key contract checks
- typed optional subphase semantics
- context/inferred-context invariants
- stimulus-type semantics for differential acquisition

### 5) Ownership Guard Extension
Updated:
- `virtual_shaping_lab/experiment/config.py`
- `tests/test_config.py`
- `tests/test_parameter_ownership_guards.py`

Behavior:
- template-param leakage guards now apply to canonical template-backed phase keys
- single-phase and multi-phase payload paths both enforce leakage boundaries

### 6) Visualization Warning Hardening
Updated:
- `virtual_shaping_lab/analysis/visualizations/summation.py`
- `virtual_shaping_lab/analysis/visualizations/probe_bar.py`
- `tests/test_visualizations.py`
- `tests/test_verification_report.py`

Behavior:
- plotting now sets fixed tick positions before tick labels
- warning-regression tests assert key report/plot flows do not reintroduce `set_ticklabels()` warnings

---

## Validation

Representative gates run during V2.13:
- `python -m pytest -q tests/test_phases.py tests/test_template_spec_versioning.py`
- `python -m pytest -q tests/test_template_strategy_guards.py`
- `python -m pytest -q tests/v2_11_contract/test_plan_determinism.py tests/test_template_determinism.py`
- `python -m pytest -q tests/v2_11_contract/test_template_record_semantics.py`
- `python -m pytest -q tests/test_config.py tests/test_parameter_ownership_guards.py`
- `python -m pytest -q tests/test_visualizations.py tests/test_full_payloads.py`
- `python -m pytest -q tests/test_visualizations.py tests/test_verification_report.py`

Closeout gate:
- `python -m pytest -q`

---

## Net State After V2.13

- template contracts are explicitly versioned and validated
- template mechanics composition cannot silently drift via unknown strategies
- template-backed runtime behavior is covered by deterministic invariants
- template record contract checks are stricter and analysis-safe
- canonical template-backed params honor ownership boundaries consistently
- known plotting warning regressions are now fixed and test-enforced
