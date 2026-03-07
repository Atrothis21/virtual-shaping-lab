# UI Version Mismatch Behavior (First-Pass)

## Purpose
Define deterministic UI behavior when backend version fields do not match client expectations.

Fields covered:
- `catalog_version`
- `record_schema_version`
- `template_version_used`

This document translates policy into concrete UI actions.

## Global Rules
- Every mismatch message must include:
  - mismatch field name
  - expected version/range (if known)
  - received version
  - next action
- Warnings are non-blocking unless explicitly marked as blocking below.
- Blocking states must still allow navigation back to stable surfaces (presets/catalog/help).

## Mismatch Matrix

### 1) `catalog_version` mismatch
- Severity:
  - warning by default
  - escalates to blocking only if refresh fails and required catalog data is unavailable
- UI action:
  - show top-level warning banner on builder/preset surfaces
  - invalidate catalog cache and trigger refresh
  - revalidate builder draft against refreshed catalog
- Refresh behavior:
  - automatic refresh attempt once
  - expose manual retry action if automatic refresh fails
- Dismissibility:
  - dismissible only after successful refresh and revalidation
  - non-dismissible while stale catalog is actively invalidating draft/plan
- Artifact access:
  - unaffected for existing run/report artifacts

### 2) `record_schema_version` mismatch
- Severity:
  - blocking for schema-dependent run detail/report rendering
- UI action:
  - show blocking error panel on affected screen
  - hide/disable schema-dependent widgets and views
  - keep schema-independent run metadata/status visible if available
- Refresh behavior:
  - no silent auto-refresh loop
  - offer manual refresh and "open stable artifact" fallback
- Dismissibility:
  - non-dismissible while mismatch persists
- Artifact access:
  - allow direct download/open for static artifacts when available
  - block interactive parsing/rendering that requires incompatible schema

### 3) `template_version_used` mismatch
- Severity:
  - degraded mode with warning
- UI action:
  - render report shell and artifact links
  - disable unsupported interactive template-dependent controls
  - show compatibility warning with fallback explanation
- Refresh behavior:
  - manual refresh/reload action
  - no hard block unless combined with schema mismatch
- Dismissibility:
  - dismissible for current session once user acknowledges
- Artifact access:
  - preserve static artifact access
  - interactive augmentations may be disabled

## Error/Banner Message Templates

### Warning template
- Title: `Version mismatch detected`
- Body:
  - `Field: <field_name>`
  - `Expected: <expected_version>`
  - `Received: <received_version>`
  - `Action: <refresh/update/fallback guidance>`

### Blocking template
- Title: `Incompatible data version`
- Body:
  - `This view cannot be rendered with the current <field_name> value.`
  - `Expected: <expected_version>`
  - `Received: <received_version>`
  - `Use manual refresh or open static artifacts.`

## First-Pass UX Contract
- Client must not silently reinterpret incompatible versions.
- Degraded/blocked states must always provide a clear recovery path.
- Mismatch handling must be consistent with `docs/ui_contract_manifest.md` and `docs/ui_error_handling_matrix.md`.
