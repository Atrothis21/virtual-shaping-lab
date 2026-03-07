# V2.17.1 Summary - Preset Entry Flow and SOC Hardening

## Overview
V2.17.1 delivers a preset-first entry workflow with lightweight phenomenon support, actionable lifecycle shortcuts, themed scientific presentation, and stronger separation-of-concerns boundaries.

Primary outcomes:
- presets browser and detail flow now function as the primary entry path
- preset selection seeds constrained draft state for builder/run/report handoff
- resolve/run/report shortcuts are wired to real API lifecycle calls
- phenomenon support is integrated as scoped metadata guidance (not teaching-mode expansion)
- preset and phenomenon surfaces now use semantic scientific theming
- preset read models and preset action side effects are extracted into dedicated modules

---

## Delivered Changes

### 1) Preset Discovery + Detail Workflow
Updated:
- `virtual_shaping_lab/ui/js/react/index_app.jsx`

Added:
- catalog-backed presets browsing (search/filter/sort)
- preset detail panel with primary actions:
  - Resolve Preset
  - Resolve + Run
  - Resolve + Run + Report

### 2) Preset/Phemonenon Seed -> Draft Handoff
Updated:
- `virtual_shaping_lab/ui/js/react/index_app.jsx`

Behavior:
- preset selection seeds constrained draft state via `DRAFT_EDITED`
- seeded state is surfaced in builder handoff status
- ownership rules preserved through state-domain boundary dispatch

### 3) Resolve/Run/Report Preset Action Flow
Updated:
- `virtual_shaping_lab/ui/js/react/index_app.jsx`

Behavior:
- preset resolve path calls `POST /plan`
- preset run path calls `POST /run`
- shortcut report path calls `POST /runs/{run_id}/report`
- explicit action-level loading/success/error state shown in preset detail
- run-readiness handling added before report creation
- mismatch/recovery messaging added for plan-hash mismatch and deferred-report scenarios

### 4) Themed Scientific Preset + Phenomenon UI
Updated:
- `virtual_shaping_lab/ui/index.html`
- `virtual_shaping_lab/ui/js/react/index_app.jsx`

Added:
- semantic protocol accent rails on cards/panels
- semantic signal chips (`cs-plus`, `cs-minus`, `probe`, `compound`, `learning`)
- improved metadata typography for preset/phenomenon info
- scoped phenomenon support styling aligned to scientific dashboard language

### 5) SOC Hardening - Read Models and Action Services
Added:
- `virtual_shaping_lab/ui/js/react/preset_read_models.js`
  - preset adapters/selectors/filter/sort selection API
- `virtual_shaping_lab/ui/js/react/preset_action_service.js`
  - workflow service boundary for resolve/run/report side effects

Updated:
- `virtual_shaping_lab/ui/js/react/index_app.jsx`
  - route container consumes read-model module
  - `AppShell` uses service-created action handlers
- `virtual_shaping_lab/ui/index.html`
  - script load order includes read-model and action-service modules

---

## Test Coverage

Added:
- `tests/test_ui_preset_read_models_scaffold.py`
- `tests/test_ui_preset_action_service_scaffold.py`

Updated:
- `tests/test_ui_presets_browser_scaffold.py`
- `tests/test_ui_preset_seed_handoff_scaffold.py`
- `tests/test_ui_preset_action_flow_scaffold.py`
- `tests/test_ui_route_scaffold.py`

Representative gates passed during implementation:
- `python -m pytest -q tests/test_ui_presets_browser_scaffold.py tests/test_ui_preset_seed_handoff_scaffold.py tests/test_ui_route_scaffold.py`
- `python -m pytest -q tests/test_ui_presets_browser_scaffold.py tests/test_ui_preset_action_flow_scaffold.py tests/test_ui_route_scaffold.py`
- `python -m pytest -q tests/test_ui_preset_read_models_scaffold.py tests/test_ui_preset_action_service_scaffold.py tests/test_ui_preset_action_flow_scaffold.py tests/test_ui_presets_browser_scaffold.py tests/test_ui_route_scaffold.py`

---

## Net State After V2.17.1

- presets are now a working, themed primary entry flow
- phenomenon metadata support is present, scoped, and non-invasive
- lifecycle shortcut actions are real API-backed flows with explicit recovery states
- UI code is more maintainable through adapter + service boundaries
- route/container logic is thinner and more declarative
