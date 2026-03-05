# V2.14 Summary - CI Simplification and Legacy-Test Retirement

## Overview
V2.14 realigns test/CI ownership to architecture-critical truth (guards, contracts, behavioral signatures), retires duplicate legacy-era tests, and introduces warning-quality enforcement for critical suites.

Primary outcomes:
- built and maintained a replacement-backed test ownership matrix
- retired obsolete/duplicate hardcut-era tests after replacement coverage was in place
- formalized CI into ordered architecture buckets
- added a temporary non-blocking full-suite compare job for parity confidence
- added warning-quality gating (`-W error`) with explicit transitional allowlist governance

---

## Delivered Changes

### 1) Test Ownership Matrix + Retirement Mapping
Added/updated:
- `V2.14_test_ownership_matrix.md`

Coverage:
- classifies tests by `guard`, `contract`, `behavioral`, `unit/internal`
- records replacement coverage for every retirement candidate
- documents retirement decisions made in V2.14

### 2) Legacy/Duplicate Test Retirement
Removed:
- `tests/test_experiment_hardcut_guards.py`
- `tests/test_v2_architecture_sanity.py`

Replacement coverage retained through:
- `tests/v2_11_guards/test_no_legacy_shim_paths_guard.py`
- `tests/test_agents.py`
- `tests/test_learners.py`
- `tests/test_representations.py`
- `tests/v2_11_guards/*`
- `tests/v2_11_contract/*`

### 3) Guard Suite Cleanup
Updated:
- `tests/v2_11_guards/test_no_legacy_shim_paths_guard.py`

Behavior:
- removed obsolete self-skip references to retired test files
- preserved hardcut import-path protection in canonical guard suite

### 4) CI Bucket Formalization
Updated:
- `.github/workflows/ci.yml`

New blocking architecture flow:
1. `tests/v2_11_guards`
2. `tests/v2_11_contract`
3. `tests/behavioral_signatures`
4. selected unit slices:
   - `tests/test_run_api_contract.py`
   - `tests/test_api_contract_snapshots.py`
   - `tests/test_visualizations.py`

Temporary parity compare:
- `full_suite_compare` job retained with `continue-on-error: true`

### 5) Warning-Quality Policy
Added:
- `.github/warning_allowlist_architecture.md`

Updated:
- `.github/workflows/ci.yml` architecture-bucket commands now run with:
  - `-W error`
  - one explicit transitional `DeprecationWarning` allowlist entry for `experiment.factories.phase_factory`

### 6) Architecture Documentation Refresh
Updated:
- `docs/core_engine_architecture.md`

Added V2.14 test/CI governance section:
- bucket order and intent
- transitional compare-job semantics
- warning policy and allowlist ownership
- retirement policy linkage to ownership matrix

---

## Validation

Representative gates executed during V2.14:
- `python -m pytest -q tests/v2_11_guards tests/v2_11_contract tests/behavioral_signatures`
- `python -m pytest -q tests/v2_11_guards tests/v2_11_contract tests/test_import_boundaries.py`
- `python -m pytest -q tests/test_agents.py tests/test_learners.py tests/test_representations.py tests/behavioral_signatures`
- `python -m pytest -q tests/v2_11_guards tests/v2_11_contract tests/behavioral_signatures tests/test_run_api_contract.py tests/test_api_contract_snapshots.py tests/test_visualizations.py -W error -W "default:experiment.factories.phase_factory is a compatibility shim; use experiment.phases.catalog_runtime or experiment.phases.public.:DeprecationWarning"`

Closeout gate:
- `python -m pytest -q`

---

## Net State After V2.14

- architecture-critical CI now runs as explicit guard/contract/behavior buckets
- warning regressions are CI-visible and fail-fast by default
- legacy-only duplicate tests removed with documented replacement mapping
- full-suite parity is still monitored via temporary non-blocking compare job
- core architecture docs now describe test governance as a first-class runtime concern
