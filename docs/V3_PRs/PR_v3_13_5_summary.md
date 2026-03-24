# V3.13.5 Summary - Runtime Operator Realization and Report Coupling

## Overview
V3.13.5 aligns runtime execution and report generation with first-class operator-basis contracts so declared stages and readouts are realized consistently and deterministically.

Primary outcomes:
- added explicit runtime stage realization semantics (`executed`, `delegated`, `metadata_only`)
- added stage-level diagnostics surfaces in run metadata and regeneration metadata
- bound operator stage TrialState I/O to registry IDs with strict unknown-field rejection
- added per-run operator stage I/O provenance artifacts with deterministic hashes
- moved report alignment mapping to registry-driven `m` readout metadata and removed hand-authored metric maps
- enforced strict missing-readout failure behavior when measurement selections are provided
- added deterministic report-alignment hash artifacts and collision-safe report directory creation
- added basis-driven replay determinism checks for acquisition materialized paths
- published runtime/report coupling contract docs and wired a dedicated blocking CI bucket

This slice closes the runtime/report coupling gap between basis declaration and emitted artifacts.

---

## Slice 1 - Declared Operator Realization Matrix

### Objective
Emit explicit realization state for declared operator stages and expose diagnostics in run metadata.

### Implemented
Updated:
- `virtual_shaping_lab/experiment/runner.py`
- `virtual_shaping_lab/api/services.py`
- `tests/test_v3_runner_environment_integration.py`
- `tests/test_run_api_contract.py`

Changes:
- runtime records now include stage realization matrix and non-executing declared stages
- run metadata now includes aggregated `operator_stage_diagnostics`
- regenerated report metadata preserves stage diagnostics from source runs

---

## Slice 2 - TrialState I/O Contract Binding

### Objective
Bind runtime stage read/write declarations to TrialState registry IDs and persist provenance.

### Implemented
Updated:
- `virtual_shaping_lab/api/services.py`
- `tests/test_run_api_contract.py`

Changes:
- added stage-to-operator I/O binding against TrialState registry field IDs
- added strict unknown-field rejection during run execution
- added `operator_stage_io_provenance.json` artifact with stable `io_provenance_hash`
- ensured regenerated reports preserve I/O provenance artifact

---

## Slice 3 - Measurement (`m`) to Report Alignment

### Objective
Make report alignment driven by `m` readout selections using registry-only metadata.

### Implemented
Updated:
- `virtual_shaping_lab/ui/contracts/operator_basis_registry.py`
- `virtual_shaping_lab/ui/contracts/report_alignment.py`
- `virtual_shaping_lab/ui/contracts/preset_registry.py`
- `virtual_shaping_lab/analysis/report/report.py`
- `virtual_shaping_lab/ui/contracts/__init__.py`
- `tests/test_v3_ui_report_alignment.py`

Changes:
- added `m` readout-to-metric alignment metadata in basis registry
- removed hardcoded metric-to-variable alignment table from report alignment path
- added deterministic multi-readout priority resolution
- added strict missing-readout failure when measurement selections are provided
- added tests for missing-readout rejection, ordering determinism, and no-hand-authored-map assertions

---

## Slice 4 - Runtime/Report Determinism Pass

### Objective
Harden runtime/report artifact determinism and collision safety.

### Implemented
Updated:
- `virtual_shaping_lab/analysis/report/report.py`
- `virtual_shaping_lab/ui/contracts/report_alignment.py`
- `virtual_shaping_lab/ui/contracts/__init__.py`
- `virtual_shaping_lab/api/services.py`
- `tests/test_v3_ui_report_alignment.py`
- `tests/test_v3_rollout_replay_harness.py`
- `tests/test_run_api_contract.py`

Changes:
- report directories now use collision-safe timestamp suffixing (`_01`, `_02`, ...)
- report alignment now emits deterministic hash artifacts:
  - `report_alignment_identity.json`
  - `report_alignment.sha256`
- API artifacts now include report-alignment identity/hash paths when present
- added basis-materialized acquisition replay determinism test coverage

---

## Slice 5 - Runtime Coupling Hardening

### Objective
Finalize docs and blocking CI coverage for runtime/report coupling contracts.

### Implemented
Added:
- `docs/v3_runtime_report_operator_coupling.md`
- `docs/v3_14_stage_realization_migration_notes.md`

Updated:
- `.github/workflows/ci.yml`

Changes:
- documented runtime vs metadata-only stage behavior contract
- documented deterministic artifact and alignment identity surfaces
- documented V3.14+ migration path for stage realization expansion
- added blocking CI bucket:
  - `Run V3 runtime/report operator coupling`

---

## Closeout Impact

After V3.13.5:
- declared operator-basis selections are reflected in runtime and report metadata surfaces
- `m` selections are first-class report alignment inputs
- report alignment mapping is registry-driven and not hand-authored in preset/editor logic
- runtime/report artifacts are deterministic, collision-safe, and traceable to basis identity
- acquisition and differential-acquisition runtime/report paths retain determinism under coupling checks

V3.13.5 therefore closes the runtime/report coupling milestone for basis-driven execution.

---

## Validation

### Slice and Coupling Gates
Validated via:
- `tests/test_v3_runner_environment_integration.py`
- `tests/test_v3_ui_report_alignment.py`
- `tests/test_v3_rollout_replay_harness.py`
- `tests/test_run_api_contract.py`
- `tests/test_v3_operator_pipeline_types.py`
- `tests/test_v3_trial_state.py`

### CI-Facing Contract Checks
Validated by assertions that:
- stage realization and non-executing stage diagnostics are emitted and preserved
- stage I/O provenance is registry-validated and artifactized
- `m` readout mapping is registry-driven with strict coverage failures when requested
- report alignment hash artifacts are deterministic
- report output directories are collision-safe under timestamp ties

---

## Net State After V3.13.5

- runtime/report coupling contracts are explicit and test-enforced
- report alignment is readout-registry-driven with deterministic priority behavior
- deterministic provenance and alignment identities are emitted for run and regeneration paths
- blocking CI coverage now exists for runtime/report coupling regressions

V3.13.5 establishes the hard runtime/report contract boundary for V3.14 expansion work.

## Validation Commands

Targeted gates exercised during implementation:
- `python -m pytest -q tests/test_v3_runner_environment_integration.py`
- `python -m pytest -q tests/test_v3_ui_report_alignment.py`
- `python -m pytest -q tests/test_v3_rollout_replay_harness.py`
- `python -m pytest -q tests/test_run_api_contract.py -k "run_api_contract_fixtures or regenerates_report or operator_stage_io_provenance"`
- `python -m pytest -q tests/test_v3_operator_pipeline_types.py tests/test_v3_trial_state.py tests/test_v3_runner_environment_integration.py tests/test_v3_ui_report_alignment.py tests/test_v3_rollout_replay_harness.py`
