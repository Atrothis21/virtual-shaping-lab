## Overview
This PR closes out V2.3 as an architecture-hardening release across protocols, analysis, and behavioral validation.

Primary outcomes:
- protocol registration moved to an explicit compositional catalog
- analysis defaults moved to compositional, versioned template specs
- protocol-to-analysis execution gained a default template runner path
- behavioral signature coverage expanded (including operant FI/FR proxy)
- behavioral signatures are now explicit CI gates
- protocol key lookup behavior is normalized consistently across runtime and analysis layers
- fallback template behavior is explicit and actionable
- core engine architecture documentation added

---

## What Was Delivered

### 1) Protocol Catalog Architecture
Added:
- `virtual_shaping_lab/protocols/catalog.py`
  - `PROTOCOL_BUILDERS`
  - `available_protocols()`
  - `validate_protocol_name()`
  - `build_protocol(...)`

Updated:
- `virtual_shaping_lab/protocols/__init__.py` exports
- `virtual_shaping_lab/experiment/factories/protocol_factory.py` to use catalog-backed registry

Tests:
- `tests/test_protocol_catalog.py`

Result:
- protocol extension surface is centralized and directly testable.

### 2) Analysis Template Composition
Added:
- `ReportTemplateSpec` in `virtual_shaping_lab/analysis/domain/types.py`

Extended:
- `virtual_shaping_lab/analysis/report/catalog.py`
  - `DEFAULT_TEMPLATE_BY_PROTOCOL`
  - `FALLBACK_TEMPLATE`
  - `get_default_template_for_protocol(...)`

Added:
- `run_protocol_default_report(...)` in `virtual_shaping_lab/analysis/registry.py`

Tests:
- `tests/test_analysis_report_catalog.py`
- `tests/test_analysis_registry.py`

Result:
- protocol-to-analysis defaults are now compositional (`report + metrics + figures`) instead of string-only mappings.

### 3) Behavioral Signature Expansion
Added:
- `tests/behavioral_signatures/test_fi_vs_fr.py`

Behavior:
- qualitative schedule-level proxy signature comparing FR-1 and FI-10 reinforcement density
- wording explicitly clarifies this is a proxy under current operant semantics (not canonical FI scallop proof)

Result:
- operant schedule behavior is now covered in the behavioral-signature suite.

### 4) Catalog Robustness + Closeout Refinements
Added:
- `template_version: int = 1` in `ReportTemplateSpec`
- shared normalizer `virtual_shaping_lab/domain/naming.py`
  - `normalize_protocol_key(...)`

Normalization applied in:
- `virtual_shaping_lab/protocols/catalog.py`
- `virtual_shaping_lab/analysis/report/catalog.py`
- `virtual_shaping_lab/experiment/factories/protocol_factory.py`

Fallback ergonomics improved in analysis catalog:
- warning now includes:
  - requested protocol key
  - normalized key
  - available mappings

Tests updated:
- `tests/test_analysis_report_catalog.py`
- `tests/test_protocol_catalog.py`
- `tests/test_factories.py`

Result:
- key lookup is consistent across layers and fallback behavior is explicit/actionable.

### 5) CI Behavioral Gating
Updated:
- `.github/workflows/ci.yml`

Added explicit gate:
- `pytest -q tests/behavioral_signatures`

Then full suite still runs.

Result:
- behavioral signatures are first-class CI regressions gates.

### 6) Architecture Documentation
Added:
- `docs/core_engine_architecture.md`

Covers:
- layered core engine architecture
- runtime control flow
- extension surfaces
- known gaps and next milestones

Result:
- V2.3 architecture state is documented for implementation and planning continuity.

---

## Validation

Targeted gates run during implementation included:
- `python -m pytest -q tests/behavioral_signatures/test_fi_vs_fr.py tests/test_analysis_report_catalog.py`
- `python -m pytest -q tests/test_protocol_catalog.py tests/test_factories.py tests/test_protocols.py`
- `python -m pytest -q tests/test_analysis_report_catalog.py tests/test_analysis_registry.py tests/test_verification_report.py`
- `python -m pytest -q tests/behavioral_signatures`
- `python -m pytest -q tests/test_factories.py tests/test_protocol_catalog.py tests/test_analysis_report_catalog.py`

Final full sweep:
- `python -m pytest -q` passed.

Note:
- existing visualization warnings (tick label warnings in plotting code) remain; no test failures.

---

## Net Architectural State After V2.3

- protocol assembly now has a dedicated compositional catalog surface
- analysis defaults now use compositional, versioned template specs
- protocol->analysis execution has a reusable default runner path
- protocol-key normalization is consistent across protocol/factory/analysis boundaries
- missing template mappings are explicit warnings (not silent)
- behavioral signatures are enforced as explicit CI gates
- core engine architecture is documented with current gaps

---

## Out of Scope (Deferred to V2.4)

- true tick-native operant schedule semantics for FI/VI/VR
- canonical within-trial FI hallmark/scallop behavioral signatures replacing current schedule-level proxy checks
