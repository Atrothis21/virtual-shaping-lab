# V2.9 Phase 1 Inventory: Canonical Template Migration

## Purpose
This inventory identifies remaining legacy classical phase-class usage and classifies each path for V2.9 migration policy.

Classification labels:
- `migrate_now`: canonical parameter-only path should move to template-backed construction.
- `keep_custom`: true control-flow/special-case class path remains class-based.

## Remaining Legacy Classical Paths (Protocol-Level)

| Protocol key | Current phase construction path | Legacy phase keys/classes in use | Required subphase naming invariants | Classification |
| --- | --- | --- | --- | --- |
| `extinction` | Direct class instantiation in `protocols/extinction.py` | `AcquisitionPhase`, `NonReinforcementPhase` | Must preserve `acquisition`, `nonreinforcement` (`tests/behavioral_signatures/test_extinction_reacquisition.py`, `tests/test_behavioral_phenomena_defaults.py`) | `migrate_now` |
| `rapid_reacquisition` | Direct class instantiation in `protocols/rapid_reacquisition.py` | `AcquisitionPhase`, `NonReinforcementPhase`, plus `ContextShiftPhase` control points | Preserve current phase names as emitted today (`acquisition`, `nonreinforcement`, context shifts). No explicit behavioral-name assertions currently, but keep record compatibility. | `migrate_now` for canonical classical phases; `keep_custom` for context shift units |
| `occasion_setting` | Direct class instantiation in `protocols/occasion_setting.py` | `AcquisitionPhase`, `NonReinforcementPhase`, `ProbePhase` | Preserve `acquisition`, `nonreinforcement`, `probe` naming in records for analysis/report continuity | `migrate_now` |

## Canonical Legacy Phase Keys Still Exposed in Factory

These keys currently resolve to class-based canonical Pavlovian phases in `experiment/factories/phase_factory.py`:
- `acquisition`
- `nonreinforcement`
- `compound_acquisition`
- `compound_nonreinforcement`
- `differential_acquisition`
- `probe`

Template-backed equivalents already exist:
- `acquisition_template`
- `nonreinforcement_template`
- `compound_acquisition_template`
- `compound_nonreinforcement_template`
- `differential_acquisition_template`
- `probe_template`

Classification:
- canonical keys above: `migrate_now` (template-first default target)

## Special-Case Custom Class Phases (Remain Class-Based)

From `experiment/phases/catalog.py` allowlist and current runtime behavior:
- `context_shift`
- `criterion_shift`

These are control-flow/special-case phases and remain `keep_custom`.

## Protocols Already Template-Backed (No Action in Phase 1)

Confirmed template-backed canonical composition:
- `blocking`
- `conditioned_inhibition`
- `aab_renewal`
- `aba_renewal`
- `abc_renewal`

## Migration Checklist for Phase 2

1. Switch `extinction` protocol phase construction to template variants while preserving `acquisition`/`nonreinforcement` names.
2. Switch canonical classical portions of `rapid_reacquisition` to template variants; retain class-based `context_shift`.
3. Switch `occasion_setting` protocol to template variants while preserving `acquisition`/`nonreinforcement`/`probe` names.
4. Keep factory compatibility for legacy keys, but make template-backed path the default authoring intent.
