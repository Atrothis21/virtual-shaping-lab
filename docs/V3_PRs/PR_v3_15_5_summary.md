# V3.15.5 Summary - Arrangement-Task-Agent UI/API Cutover

## Overview
V3.15.5 completes the tuple-first authoring cutover surface for `(arrangement, task, agent)` across contracts, API endpoints, UI flow scaffolding, runtime/report identity propagation, and migration boundary hardening.

Primary outcomes:
- introduced tuple-first authoring payload contract (`tuple_v1`) with compatibility translation from legacy preset-route payloads
- added tuple-guided catalog and tuple materialization API surfaces
- added UI tuple selection flow contract with explicit hidden-vs-disabled agent visibility policy
- propagated tuple identity through `/run` metadata, regenerated report metadata, and `artifact_identity.json`
- hardened migration boundaries for legacy canonicalization bridge behavior and deprecated tuple-route input diagnostics
- added blocking CI coverage for the V3.15.5 tuple cutover surface

This slice moves authoring from preset-first inputs toward first-class tuple semantics while preserving compatibility wrappers and explicit migration diagnostics.

---

## Slice 1 - Authoring Payload Contract Shift

### Objective
Define tuple-first authoring payload shape and compatibility translator.

### Implemented
Added:
- `virtual_shaping_lab/ui/contracts/tuple_authoring_contract.py`
- `tests/test_v3_tuple_authoring_contract.py`

Updated:
- `virtual_shaping_lab/ui/contracts/__init__.py`

Changes:
- added tuple payload contract fields:
  - `arrangement`
  - `task`
  - `agent`
  - `edits`
- added explicit contract identity:
  - `contract_version = 3.15.5`
  - `authoring_mode = tuple_v1`
- added legacy `preset_id` translator with diagnostics:
  - translated tuple
  - legacy preset label
  - translation quality (`lossless` / `heuristic`)
  - deprecation diagnostics

---

## Slice 2 - API Composition/Materialization Endpoints

### Objective
Expose tuple-driven API catalog/materialization paths and preserve compatibility wrappers.

### Implemented
Added:
- `virtual_shaping_lab/ui/contracts/tuple_authoring_api.py`
- `tests/test_v3_tuple_authoring_api.py`

Updated:
- `virtual_shaping_lab/ui/contracts/__init__.py`
- `virtual_shaping_lab/api/run.py`

Changes:
- added tuple API endpoints:
  - `GET /catalog/tuple-authoring`
  - `POST /catalog/tuple-authoring/materialize`
- guided catalog now returns:
  - arrangements
  - task availability by arrangement
  - agent availability by tuple
  - projected editable fields
- materialization now composes tuple -> operator subset -> canonical payload with composed subset identity
- preserved preset basis endpoints as compatibility wrappers

---

## Slice 3 - UI Flow Refactor (3-Step Selection)

### Objective
Implement tuple selection flow contract for arrangement -> task -> agent.

### Implemented
Added:
- `virtual_shaping_lab/ui/js/react/tuple_authoring_flow.jsx`
- `tests/test_v3_ui_tuple_selection_flow.py`
- `tests/test_v3_ui_tuple_visibility_policy.py`

Changes:
- added tuple flow step model:
  1. arrangement
  2. task
  3. agent
- added explicit visibility policy:
  - hide structurally impossible agents
  - show disabled behaviorally invalid/partial agents with reasons
- added registry-generated selectable universe marker and contract-level UI assertions

---

## Slice 4 - Runtime/Metadata Identity Integration

### Objective
Carry tuple identity through run/report metadata and persisted artifacts.

### Implemented
Updated:
- `virtual_shaping_lab/api/services.py`
- `virtual_shaping_lab/analysis/report/report.py`
- `tests/test_run_api_contract.py`

Changes:
- added `tuple_authoring_identity` propagation for:
  - `/run` response metadata
  - run status metadata
  - report regeneration metadata
  - report payload provenance
- persisted tuple identity in `artifact_identity.json`
- added parity assertions for run vs artifact vs regenerated report identities
- fixed tuple identity regeneration test fixture to avoid unrelated operant policy-schema failure path

---

## Slice 5 - Bridge Hardening and Migration Boundaries

### Objective
Harden bridge behavior and migration diagnostics on tuple cutover routes.

### Implemented
Updated:
- `virtual_shaping_lab/ui/js/react/teaching_panel.jsx`
- `virtual_shaping_lab/api/run.py`
- `tests/test_ui_teaching_contract.py`
- `tests/test_v3_tuple_authoring_api.py`

Changes:
- added explicit migration boundary model in teaching panel:
  - `TUPLE_ROUTE_MIGRATION_STRATEGY = overlay_gradual`
  - `TUPLE_MIGRATED_PRESET_ROUTES`
  - unified `LEGACY_BRIDGE_DISABLED_PRESET_ROUTES`
- preserved explicit fallback for non-migrated routes
- added tuple-route migration diagnostics on deprecated tuple materialization input (`preset_id` shape)
- added tests for bridge boundary mapping and deprecated-shape diagnostics

---

## Completion Pass

### Objective
Close CI/test/exit-criteria gaps for V3.15.5.

### Implemented
Updated:
- `.github/workflows/ci.yml`
- `V3_15_5_plan.md`

Changes:
- added blocking CI bucket:
  - `Run V3 arrangement-task-agent cutover`
- wired tuple cutover gates:
  - tuple authoring contract/API tests
  - tuple UI flow/visibility tests
  - run/report tuple identity propagation tests
  - bridge + tuple migration boundary tests
- aligned plan testing/exit criteria to selected migration strategy (`overlay_gradual`)

---

## Closeout Impact

After V3.15.5:
- tuple-first authoring is available as a first-class API/contract surface
- tuple-guided catalog and tuple materialization are domain-shaped and compatibility-aware
- tuple identity is traceable end-to-end through run artifacts and regenerated reports
- migration boundary behavior is explicit, tested, and diagnostics-backed
- CI blocks regressions across tuple contract, API, UI flow policy, and identity propagation

V3.15.5 therefore completes the tuple cutover boundary needed before broader route migration in V3.16.x.

---

## Validation

### Slice and Cutover Gates
Validated via:
- `tests/test_v3_tuple_authoring_contract.py`
- `tests/test_v3_tuple_authoring_api.py`
- `tests/test_v3_ui_tuple_selection_flow.py`
- `tests/test_v3_ui_tuple_visibility_policy.py`
- `tests/test_run_api_contract.py`
- `tests/test_ui_teaching_contract.py`

### CI-Facing Contract Checks
Validated by assertions that:
- tuple payloads and legacy translation diagnostics are schema-valid and deterministic
- guided tuple catalog filters task/agent options correctly by tuple context
- UI tuple flow honors hidden-vs-disabled visibility policy
- tuple identity persists across run metadata, artifact identity, and report regeneration
- migrated-route bridge boundaries and deprecated-shape diagnostics remain explicit and enforced

---

## Net State After V3.15.5

- tuple-first authoring contract/API surfaces are implemented and test-covered
- tuple selection flow policy scaffolding is in place
- tuple provenance identity is persisted across runtime/report artifacts
- migration boundary strategy (`overlay_gradual`) is encoded and tested
- blocking CI coverage exists for arrangement-task-agent cutover regressions

V3.15.5 establishes the stabilized tuple cutover boundary for route expansion and deeper UI migration in V3.16.x.

## Validation Commands

Targeted gates exercised during implementation:
- `python -m pytest -q tests/test_v3_tuple_authoring_contract.py`
- `python -m pytest -q tests/test_v3_tuple_authoring_api.py`
- `python -m pytest -q tests/test_v3_ui_tuple_selection_flow.py`
- `python -m pytest -q tests/test_v3_ui_tuple_visibility_policy.py`
- `python -m pytest -q tests/test_run_api_contract.py -k "tuple_identity or regeneration_keeps_tuple_identity or arrangement or task or agent or composition_hash"`
- `python -m pytest -q tests/test_ui_teaching_contract.py -k "legacy_bridge or tuple_route_migration"`
