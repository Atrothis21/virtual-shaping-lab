# V3.11.0 Summary - Explainability and TrialState-Linked Results

## Overview
V3.11.0 wires results, overlays, and report-facing explainability surfaces directly to V3 UI registries, so dependent variables, operators, and TrialState fields remain traceable through one contract stack.

Primary outcomes:
- added a dependent-variable resolver layer shared across results and report surfaces
- added registry-driven trial-hover explainability panel assembly
- added operator-to-graph backlink contracts with cross-registry integrity enforcement
- added grouped TrialState inspector with mode-based visibility policies
- added report-alignment contracts so report metric labels/descriptions can resolve from dependent-variable metadata
- added blocking CI coverage for the V3.11 explainability contract suite

This slice establishes a registry-first explainability path from trial internals to results/report presentation.

---

## Slice 1 - Dependent Variable Resolver Layer

### Objective
Provide a shared resolver from dependent-variable IDs to labels/charts/visibility/semantics for results/report consumers.

### Implemented
Added:
- `virtual_shaping_lab/ui/contracts/dependent_variable_resolver.py`

Updated:
- `virtual_shaping_lab/ui/contracts/__init__.py`

Added tests:
- `tests/test_v3_ui_dependent_variable_resolver.py`

Changes:
- added `resolve_dependent_variable(...)` and surface helpers for `results` and `report`
- added malformed metadata guards and unknown-ID failure behavior
- exposed shared resolver APIs through UI contracts facade

---

## Slice 2 - Trial Hover Explainability Overlay

### Objective
Build trial-hover explainability panels from registry hooks with prediction/outcome/error/update linkage when available.

### Implemented
Added:
- `virtual_shaping_lab/ui/contracts/trial_hover_explainability.py`

Updated:
- `virtual_shaping_lab/ui/contracts/__init__.py`

Added tests:
- `tests/test_v3_ui_trial_hover_explainability.py`

Changes:
- added hover-panel contract assembly sourced from dependent-variable explainability metadata
- added graceful degradation behavior when trial fields are missing
- enforced non-object trial-record guardrails

---

## Slice 3 - Operator-to-Graph Backlinking

### Objective
Connect operators to related dependent variables and TrialState fields with integrity checks across registries.

### Implemented
Added:
- `virtual_shaping_lab/ui/contracts/operator_graph_backlinks.py`

Updated:
- `virtual_shaping_lab/ui/contracts/__init__.py`

Added tests:
- `tests/test_v3_ui_operator_graph_backlinks.py`

Changes:
- added `resolve_operator_graph_backlinks(...)` and `list_operator_graph_backlinks(...)`
- added cross-registry backlink integrity validation including payload-based validator
- enforced consistency between operator I/O surfaces and dependent-variable explainability links

---

## Slice 4 - Expert TrialState Inspector

### Objective
Provide grouped TrialState inspection with policy-controlled visibility for preset/teaching/expert modes.

### Implemented
Added:
- `virtual_shaping_lab/ui/contracts/trialstate_inspector.py`

Updated:
- `virtual_shaping_lab/ui/contracts/__init__.py`

Added tests:
- `tests/test_v3_ui_trialstate_inspector.py`

Changes:
- added grouped inspector contract rendering from TrialState registry field groups
- enforced mode policies (`preset`, `teaching`, `expert`)
- added unsupported-mode guard behavior

---

## Slice 5 - Report Alignment Pass

### Objective
Align report metric naming with dependent-variable registry labels/descriptions and keep artifact labeling consistent with results surfaces.

### Implemented
Added:
- `virtual_shaping_lab/ui/contracts/report_alignment.py`
- `tests/test_v3_ui_report_alignment.py`

Updated:
- `virtual_shaping_lab/ui/contracts/__init__.py`
- `virtual_shaping_lab/analysis/report/report.py`

Changes:
- added report-alignment contract builder with explicit metric-to-dependent-variable mapping
- added fallback behavior for report-only presets not present in UI preset registry
- report runs now emit `report_alignment.json`
- PDF metric pages now use aligned display labels when available
- added selected-preset snapshot-style alignment checks for generated report artifacts

---

## Completion Pass - CI Gate Integration and Alignment Hardening

### Objective
Close partial items by making V3.11 explainability checks blocking in CI and hardening report-alignment tests.

### Implemented
Updated:
- `.github/workflows/ci.yml`
- `virtual_shaping_lab/ui/contracts/report_alignment.py`
- `tests/test_v3_ui_report_alignment.py`

Changes:
- added blocking CI step: `Run V3 UI explainability contracts`
- CI step runs:
  - `tests/test_v3_ui_dependent_variable_resolver.py`
  - `tests/test_v3_ui_trial_hover_explainability.py`
  - `tests/test_v3_ui_operator_graph_backlinks.py`
  - `tests/test_v3_ui_trialstate_inspector.py`
  - `tests/test_v3_ui_report_alignment.py`
- expanded mapping for stimulus-level prediction metrics to registry labels where semantically aligned
- hardened report-alignment snapshot tests for timestamp/output-root isolation and parameterized metric construction

---

## Closeout Impact

After V3.11.0:
- dependent-variable/operator/TrialState linkages are surfaced through one explainability contract stack
- hover overlays, operator backlinks, and trial inspector behavior are registry-driven and test-enforced
- report labels can resolve from the same dependent-variable metadata used by results surfaces
- CI now blocks regressions in V3.11 explainability contracts

This slice completes the explainability-and-linkage pass for the current registry architecture.

---

## Validation

### Slice and Completion Gates
Validated through:
- `tests/test_v3_ui_dependent_variable_resolver.py`
- `tests/test_v3_ui_trial_hover_explainability.py`
- `tests/test_v3_ui_operator_graph_backlinks.py`
- `tests/test_v3_ui_trialstate_inspector.py`
- `tests/test_v3_ui_report_alignment.py`

### CI-Facing Contract Checks
Validated by assertions that:
- resolver outputs remain registry-conformant across results/report surfaces
- overlay/backlink contracts remain cross-registry consistent
- TrialState inspector honors mode visibility policies
- report metric labeling remains aligned to dependent-variable metadata when mapped

---

## Net State After V3.11.0

- explainability contracts are implemented across resolver, hover, backlinks, inspector, and report alignment layers
- V3 results/report naming surfaces now share registry-driven semantics
- V3.11 explainability tests are wired into blocking CI

V3.11.0 therefore closes the explainability and TrialState-linked results milestone.

## Validation Commands

Targeted gates exercised during implementation:
- `python -m pytest -q tests/test_v3_ui_dependent_variable_resolver.py`
- `python -m pytest -q tests/test_v3_ui_trial_hover_explainability.py`
- `python -m pytest -q tests/test_v3_ui_operator_graph_backlinks.py`
- `python -m pytest -q tests/test_v3_ui_trialstate_inspector.py`
- `python -m pytest -q tests/test_v3_ui_report_alignment.py`
- `python -m pytest -q tests/test_v3_ui_dependent_variable_resolver.py tests/test_v3_ui_trial_hover_explainability.py tests/test_v3_ui_operator_graph_backlinks.py tests/test_v3_ui_trialstate_inspector.py tests/test_v3_ui_report_alignment.py`

