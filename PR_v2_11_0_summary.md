# V2.11 Summary - Legacy Hard-Cut and CI Realignment

## Overview
V2.11 completes the legacy hard-cut program started in V2.10 and aligns CI/test boundaries to the post-legacy architecture.

Primary outcomes:
- canonical classical phase keys are template-backed only
- legacy `*_legacy` phase aliases are removed from runtime phase construction
- API/import boundaries are guard-enforced and strict
- runtime/protocol code paths avoid direct factory-internal imports outside approved seams
- CI now fast-fails on V2.11 guards/contracts before behavioral/full-suite execution

---

## Delivered Changes

### 1) V2.11 Contract + Guard Spine
Added/expanded:
- `tests/v2_11_contract/*`
- `tests/v2_11_guards/*`

Hardening:
- `test_no_deep_api_imports_guard.py` moved from soft to strict
- `test_factory_boundary_usage_guard.py` moved from soft to strict
- `test_no_legacy_phase_keys_guard.py` moved from soft to strict
- `test_canonical_phase_keys_template_only.py` added for canonical-key policy enforcement

### 2) Facade-First Realignment
High-level test flows are aligned to:
- `experiment.public.*`
- `analysis.public.*`

This removes deep runtime/analysis import coupling from integration-facing tests.

### 3) Canonical Phase Key Policy Hardening
In `experiment.factories.phase_factory`:
- canonical classical keys now resolve to template-backed builders:
  - `acquisition`
  - `nonreinforcement`
  - `compound_acquisition`
  - `compound_nonreinforcement`
  - `differential_acquisition`
  - `probe`

Also enforced parity naming semantics for template-emitted canonical phase names.

### 4) Legacy Alias Removal (Hard-Cut)
Removed runtime construction aliases:
- `acquisition_legacy`
- `nonreinforcement_legacy`
- `compound_acquisition_legacy`
- `compound_nonreinforcement_legacy`
- `differential_acquisition_legacy`
- `probe_legacy`

Tests were updated to assert these aliases are removed and rejected.

### 5) Factory Quarantine Tightening
Applied single-owner/adapter cleanup:
- `protocol_factory` now aliases canonical protocol registry directly
- `reward_schedule_factory` delegates strictly to world-owned schedule builders

Added runtime import seam:
- `experiment/phases/public.py`

Protocols/phases that previously imported factories directly now import through:
- `experiment.phases.public.build_phase`
- `experiment.world.schedules.build_reward_schedule`

### 6) CI Realignment
Workflow ordering updated to fast-fail on architecture regressions:
1. `tests/v2_11_guards`
2. `tests/v2_11_contract`
3. `tests/behavioral_signatures`
4. full suite (`pytest`)

---

## Migration Table (Removed -> Replacement)

- `phase key: acquisition_legacy` -> `acquisition` (template-backed)
- `phase key: nonreinforcement_legacy` -> `nonreinforcement` (template-backed)
- `phase key: compound_acquisition_legacy` -> `compound_acquisition` (template-backed)
- `phase key: compound_nonreinforcement_legacy` -> `compound_nonreinforcement` (template-backed)
- `phase key: differential_acquisition_legacy` -> `differential_acquisition` (template-backed)
- `phase key: probe_legacy` -> `probe` (template-backed)
- `protocol import: experiment.factories.phase_factory.build_phase` -> `experiment.phases.public.build_phase`
- `schedule import: experiment.factories.reward_schedule_factory.build_reward_schedule` -> `experiment.world.schedules.build_reward_schedule`

---

## Compatibility Notes

- Browser/API lifecycle invariants remain intact:
  - `PlanDraft -> PlanResolved -> RunComplete -> ReportComplete`
- Runtime contracts remain runnable-only (`iter_steps` required).
- No silent fallback to removed legacy phase alias keys.
- Existing plotting warnings (tick-label warnings) remain non-blocking and unrelated to runtime contract correctness.

---

## Validation

Representative gates run during V2.11 closeout:
- `tests/v2_11_guards`
- `tests/v2_11_contract`
- `tests/behavioral_signatures`
- targeted suites for:
  - factories/assembly
  - protocol/runtime
  - import boundaries
  - payload/API flows

Final closeout gate:
- `python -m pytest -q`

---

## Net State After V2.11

- legacy phase alias entrypoints are removed
- canonical classical phase keys are template-only
- guard and contract suites are strict and CI-prioritized
- factory internals are quarantined behind approved seams
- runtime/test architecture is aligned to post-legacy constraints
