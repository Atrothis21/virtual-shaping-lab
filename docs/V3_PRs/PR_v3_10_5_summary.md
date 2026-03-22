# V3.10.5 Summary - Acquisition Preset Golden Path

## Overview
V3.10.5 delivers Acquisition as the production-grade reference preset for the V3 UI model, fully wired through registry contracts with strict editability and payload-boundary enforcement.

Primary outcomes:
- expanded acquisition preset schema with explicit layer/locking/editability contract fields
- added registry-driven acquisition detail contract rendering for overview/phases/operators/math
- added deterministic preset payload materialization with strict allowed-only and locked-field guardrails
- added run/results handoff contract with dependent-variable-ID-only results resolution
- added acquisition hardening contracts for trial-hover overlays, route-state persistence, and structured form errors
- added a blocking CI bucket for the V3.10.5 acquisition golden path

This slice makes Acquisition the canonical implementation template for subsequent preset migrations.

---

## Slice 1 - Acquisition Preset Schema + Registry Entry

### Objective
Add acquisition preset schema fields and enforce acquisition-specific invariants.

### Implemented
Updated:
- `virtual_shaping_lab/ui/contracts/preset_registry.py`
- `virtual_shaping_lab/ui/contracts/__init__.py`

Added tests:
- `tests/test_v3_ui_preset_schema_contracts.py`

Changes:
- extended preset schema with:
  - `template`
  - `ui_contract.layers`
  - `ui_contract.locking`
  - `ui_contract.editability`
  - `ui_contract.editability.option_constraints`
- added acquisition invariants:
  - exactly one phase
  - phase protocol must be `acquisition`
  - required operators (`phi`, `p`, `delta`, `w`, `m`) must be present
- added overlap guard for allowed vs locked parameter paths

---

## Slice 2 - Acquisition Detail Screen Contract

### Objective
Build registry-driven preset detail contract with read-only operator surface.

### Implemented
Added:
- `virtual_shaping_lab/ui/contracts/preset_detail_contract.py`

Updated:
- `virtual_shaping_lab/ui/contracts/__init__.py`

Added tests:
- `tests/test_v3_ui_teaching_contract.py`

Changes:
- added `build_preset_detail_contract(...)` for acquisition detail surfaces
- detail contract now provides:
  - overview block
  - phase blocks
  - operator cards resolved from operator registry
  - math lines from operator algebra metadata
- operator surface is explicitly read-only in preset mode

---

## Slice 3 - Editability Guardrails + Payload Materialization

### Objective
Enforce strict editability boundaries and deterministic payload materialization.

### Implemented
Added:
- `virtual_shaping_lab/ui/contracts/preset_materialization.py`

Updated:
- `virtual_shaping_lab/ui/contracts/preset_registry.py`
- `virtual_shaping_lab/ui/contracts/__init__.py`

Added tests:
- `tests/test_v3_ui_payload_materialization.py`

Changes:
- added `materialize_preset_payload(...)` with:
  - locked-field rejection
  - undeclared-edit rejection
  - option-constraint enforcement for learner variants
- added deterministic serialization/hash helpers:
  - `stable_materialized_payload_json(...)`
  - `stable_materialized_payload_hash(...)`
- added payload-boundary validator:
  - `validate_materialized_payload_boundary(...)`
- fixed validation precedence so locked edits fail as locked-field violations before undeclared-edit checks

---

## Slice 4 - Results Handoff + Dependent-Variable Defaults

### Objective
Contract run-to-results handoff and dependent-variable-first results resolution.

### Implemented
Added:
- `virtual_shaping_lab/ui/contracts/preset_run_flow.py`

Updated:
- `virtual_shaping_lab/ui/contracts/__init__.py`

Added tests:
- `tests/test_v3_ui_preset_run_flow.py`

Changes:
- added `build_preset_run_flow_contract(...)` for:
  - route sequence (`library -> detail -> run -> results`)
  - results route handoff metadata
  - materialized payload handoff
- results contract enforcement:
  - dependent-variable IDs only
  - unknown dependent-variable ID rejection
  - graph-priority behavioral/learning-first ordering guard

---

## Slice 5 - Acquisition Hardening Pass

### Objective
Add overlay, route-state, and form-error hardening contracts.

### Implemented
Added:
- `virtual_shaping_lab/ui/contracts/preset_hardening.py`

Updated:
- `virtual_shaping_lab/ui/contracts/__init__.py`

Added tests:
- `tests/test_v3_ui_preset_hardening.py`

Changes:
- added `build_trial_hover_overlay(...)`:
  - overlay content resolved from dependent-variable/operator registries
  - no preset-hardcoded operator explanation strings
- added results->config state persistence helpers:
  - `encode_results_return_state(...)`
  - `decode_results_return_state(...)`
- added structured form validation API:
  - `validate_preset_form_edits(...)`
  - returns typed error codes and field-level errors

---

## Completion Pass - CI Gate Integration

### Objective
Make acquisition golden-path contract suites blocking in CI.

### Implemented
Updated:
- `.github/workflows/ci.yml`

Changes:
- added `Run V3 acquisition preset golden path bucket`:
  - `tests/test_v3_ui_preset_schema_contracts.py`
  - `tests/test_v3_ui_teaching_contract.py`
  - `tests/test_v3_ui_payload_materialization.py`
  - `tests/test_v3_ui_preset_run_flow.py`
  - `tests/test_v3_ui_preset_hardening.py`
  - filtered with `-k acquisition`

---

## Closeout Impact

After V3.10.5:
- Acquisition is fully defined as a registry-driven preset contract stack
- editability and payload boundaries are contract-enforced and test-guarded
- run/results handoff semantics are explicit and validated
- hardening behaviors (overlay integrity, route-state, form errors) are standardized
- CI now blocks regressions in the acquisition golden path

This slice finalizes Acquisition as the canonical template for scaling the same model to additional presets.

---

## Validation

### Slice and Hardening Gates
Validated through:
- `tests/test_v3_ui_preset_schema_contracts.py`
- `tests/test_v3_ui_teaching_contract.py`
- `tests/test_v3_ui_payload_materialization.py`
- `tests/test_v3_ui_preset_run_flow.py`
- `tests/test_v3_ui_preset_hardening.py`

### CI-Facing Contract Checks
Validated by assertions that:
- acquisition schema invariants are enforced
- detail/overlay content is registry-driven
- only preset-declared editable paths are mutable
- materialized payload cannot include undeclared edits
- results contract references dependent-variable IDs only and preserves priority rules

---

## Net State After V3.10.5

- acquisition preset golden path contracts are implemented end-to-end
- registry-driven behavior is enforced across detail, materialization, results, and overlays
- boundary and safety invariants are codified and test-covered
- blocking CI coverage exists for acquisition contract regressions

V3.10.5 therefore closes the Acquisition golden-path milestone.

## Validation Commands

Targeted gates exercised during implementation:
- `python -m pytest -q tests/test_v3_ui_preset_schema_contracts.py -k acquisition`
- `python -m pytest -q tests/test_v3_ui_teaching_contract.py -k acquisition`
- `python -m pytest -q tests/test_v3_ui_payload_materialization.py -k acquisition`
- `python -m pytest -q tests/test_v3_ui_preset_run_flow.py -k acquisition`
- `python -m pytest -q tests/test_v3_ui_preset_hardening.py -k acquisition`
- `python -m pytest -q tests/test_v3_ui_preset_schema_contracts.py tests/test_v3_ui_teaching_contract.py tests/test_v3_ui_payload_materialization.py tests/test_v3_ui_preset_run_flow.py tests/test_v3_ui_preset_hardening.py -k acquisition`

