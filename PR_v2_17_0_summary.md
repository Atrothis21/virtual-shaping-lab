# V2.17.0 Summary - UI Foundation (Shell, State, Catalog, Guardrails)

## Overview
V2.17.0 establishes the React UI foundation for the refactor program:

- new app shell with first-pass route containers
- shared state domain scaffolds + transition/event helpers
- catalog bootstrap flow with version persistence
- global UI primitives for banners/blocking/errors
- theme token foundation + reusable styled primitives
- enforceable UI architecture boundary and contract guardrails

This is the foundation sprint for V2.17.1+ feature work (presets, run/report, constrained builder).

---

## Delivered Changes

## 1) App Shell + Route Container Scaffold
Updated:
- `virtual_shaping_lab/ui/js/react/index_app.jsx`
- `virtual_shaping_lab/ui/index.html`

Delivered:
- top-level shell layout (header/nav/main)
- hash-route scaffold aligned to first-pass routes:
  - `#/presets`
  - `#/builder`
  - `#/run`
  - `#/report`
  - `#/catalog-help`
- explicit route container placeholders for:
  - Presets
  - Builder
  - Run
  - Report
  - Catalog/Help

## 2) Shared State Domains + Event Scaffolding
Added:
- `virtual_shaping_lab/ui/js/react/state_domains.js`

Delivered:
- domain state initializers:
  - `builderDraftState`
  - `planState`
  - `runState`
  - `reportState`
  - `catalogCacheState`
  - `debugAdvancedState`
- domain selectors
- event constants + reducer-style transition helper (`applyUIEvent`)
- guard selectors:
  - `isPlanFreshForCurrentDraft`
  - `canRunFromState`
- encoded invalidation semantics:
  - draft edits invalidate resolved plan/report readiness
  - run start resets report context
  - catalog version drift invalidates plan freshness

## 3) Catalog Bootstrap Flow
Updated:
- `virtual_shaping_lab/ui/js/react/index_app.jsx`
- `virtual_shaping_lab/ui/index.html`

Delivered:
- app bootstrap `GET /catalog/extensions` via shared API client
- version fields stored in catalog state:
  - `catalog_version`
  - `record_schema_version`
  - `template_version_used`
- bootstrap status and versions surfaced in shell nav context

## 4) Global Error/Mismatch UI Primitives
Added:
- `virtual_shaping_lab/ui/js/react/ui_primitives.jsx`

Delivered:
- reusable `GlobalBanner`
- reusable `BlockingPanel`
- reusable `NotificationStack`
- catalog mismatch helper:
  - `buildCatalogMismatchBanner(...)`
- trigger wiring in shell for:
  - catalog mismatch warning banner
  - blocking panel when catalog bootstrap fails without usable catalog data

## 5) Theme Token Foundation + UI Primitives
Added:
- `virtual_shaping_lab/ui/js/react/ui_theme_tokens.js`
- `virtual_shaping_lab/ui/js/react/ui_foundation_primitives.jsx`

Updated:
- `virtual_shaping_lab/ui/index.html`
- `virtual_shaping_lab/ui/js/react/index_app.jsx`

Delivered:
- theme token model (base, semantic, typography, spacing, radius, elevation)
- token-backed CSS variables in shell styles
- reusable foundation primitives:
  - `PageRegion`
  - `SurfacePanel`
  - `StatusBadge`
  - `PrimaryButton`
  - `SecondaryButton`
- shell/route cards migrated to primitive usage

## 6) Enforceable UI Architecture Guardrails
Added:
- `virtual_shaping_lab/ui/js/react/architecture_boundaries.json`
- `virtual_shaping_lab/ui/js/react/ui_architecture_contracts.js`
- `tests/v2_11_guards/test_ui_v2_architecture_boundaries_guard.py`

Delivered:
- layer matrix (`shared`, `features`, `routes`)
- allowed dependency direction rules
- direct `fetch(...)` restriction to shared API client
- in-code architecture contract builders/registry for containers/hooks/services
- shell contract registry initialization as scaffold signal

---

## Test Coverage Added/Updated

Added:
- `tests/test_ui_route_scaffold.py`
- `tests/test_ui_state_domains_scaffold.py`
- `tests/test_ui_global_primitives_scaffold.py`
- `tests/test_ui_theme_tokens_scaffold.py`
- `tests/test_ui_foundation_primitives_scaffold.py`
- `tests/test_ui_architecture_contracts_scaffold.py`
- `tests/v2_11_guards/test_ui_v2_architecture_boundaries_guard.py`

Representative gates run:
- `python -m pytest -q tests/test_ui_route_scaffold.py`
- `python -m pytest -q tests/test_ui_state_domains_scaffold.py tests/test_ui_route_scaffold.py`
- `python -m pytest -q tests/test_ui_route_scaffold.py tests/test_ui_state_domains_scaffold.py tests/test_ui_global_primitives_scaffold.py`
- `python -m pytest -q tests/test_ui_route_scaffold.py tests/test_ui_state_domains_scaffold.py tests/test_ui_global_primitives_scaffold.py tests/test_ui_theme_tokens_scaffold.py`
- `python -m pytest -q tests/test_ui_route_scaffold.py tests/test_ui_state_domains_scaffold.py tests/test_ui_global_primitives_scaffold.py tests/test_ui_theme_tokens_scaffold.py tests/test_ui_foundation_primitives_scaffold.py`
- `python -m pytest -q tests/v2_11_guards/test_ui_v2_architecture_boundaries_guard.py`
- `python -m pytest -q tests/v2_11_guards/test_ui_v2_architecture_boundaries_guard.py tests/test_ui_route_scaffold.py tests/test_ui_architecture_contracts_scaffold.py`

All executed gates passed.

---

## Net State After V2.17.0

- UI now has a clear refactor shell and route ownership scaffold.
- Shared state domains and transition semantics are in place.
- Catalog/version bootstrap behavior exists and is visible.
- Global non-happy-path primitives are reusable and wired.
- Theme/token + foundation primitive systems are established.
- Architecture boundary and direct-fetch drift are guarded by tests.
