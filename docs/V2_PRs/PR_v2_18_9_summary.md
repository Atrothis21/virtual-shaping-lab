# V2.18.9 Summary - Analysis and Report Canonicalization

## Overview
V2.18.9 completes the analysis-side canonicalization pass by making report regeneration artifact-driven and tightening report-template governance around finalized V2 runtime semantics.

Primary outcomes:
- report regeneration now uses canonical on-disk artifacts instead of rebuilding plan state
- regenerated reports derive replay metadata from persisted payload and artifact identity
- analysis remains records-first and does not depend on live runtime execution during regeneration
- protocol-to-template lookup now supports optional strict mode for CI/debug enforcement
- key figure and view semantics are locked to finalized V2 behavior through explicit regressions

This slice closes the remaining V2 seam where analysis/reporting still had indirect dependence on runtime-era reconstruction rather than canonical artifacts plus records.

---

## Canonical Report Regeneration

### Artifact-Driven Replay
Report regeneration now resolves from artifacts already written by the original run:

- canonical `payload.json`
- persisted `records.json`
- resolved report template configuration
- artifact-local replay metadata

The regeneration path no longer needs to rebuild an `ExperimentPlan` in order to produce a report.

### Replay Metadata from Artifacts
Regenerated reports now derive identity and replay metadata from canonical artifact state rather than recomputing it through runtime planning helpers.

This includes:
- `plan_hash`
- `record_schema_version`
- `seed_identity`
- `mechanism_provenance`

Net effect:
- report regeneration is more reproducible
- regeneration is insulated from future runtime-plan changes
- artifact replay is a first-class analysis path rather than a runtime-adjacent shortcut

### Runtime Independence
The V2.18.9 regeneration regression explicitly proves that report regeneration does not call `build_plan(...)`.

That matters because the V2 boundary is now clearer:
- runtime executes experiments
- analysis consumes persisted artifacts

---

## Template Governance

### Optional Strict Mode
Protocol-template resolution now supports optional strict enforcement for missing mappings.

Added strict-mode behavior for:
- `get_default_report_for_protocol(...)`
- `get_default_template_for_protocol(...)`

Behavior now splits cleanly:
- default mode: warn and fall back to verification template behavior
- strict mode: raise `KeyError` with available mappings

This gives CI/debug surfaces a fail-fast option without breaking current product-mode fallback behavior.

### Fallback Stability Preserved
The fallback template contract remains intact for non-strict consumers.

So V2.18.9 does not change shipped report behavior for unmapped protocols by default; it only makes the governance boundary explicit and testable.

---

## Semantic Verification of Figures and Views

### Differential / Dual-Series Semantics
`DualTimeSeriesPlot` now has direct semantic regression coverage showing that:
- CS+ and CS- are reconstructed as separate series in differential mode
- each series uses its own compact x-axis progression
- one-sided differential records still produce the intended two-curve interpretation

This locks the figure to the finalized V2 differential-runtime semantics.

### Discrimination Semantics
`DiscriminationCurvePlot` now has regression coverage proving it tracks the running:

- mean(CS+) - mean(CS-)

over the sorted trial stream.

This prevents future regressions where the figure might silently drift to per-trial or improperly windowed discrimination behavior.

### Tick-to-Trial Aggregation Semantics
`aggregate_ticks_to_trials(...)` now has explicit coverage for:
- tick sorting before aggregation
- summed reward over ticks
- last non-null action carry-forward
- last available prediction carry-forward

This matters because multiple report and verification paths consume aggregated trial summaries as a semantic bridge from tick-native runtime output.

---

## Records-First Analysis Boundary

V2.18.9 reinforces the intended analysis boundary:

- analysis consumes records
- report regeneration consumes canonical artifacts
- analysis does not reconstruct live runtime state in order to interpret a finished run

Together with V2.18.7’s record-schema guarantees, this gives V2 a more coherent analysis architecture:
- stable records boundary
- stable artifact identity
- artifact-driven regeneration
- stricter template governance

---

## Validation

### Regeneration Gates
Validated through:
- `tests/test_report.py`
- `tests/test_verification_report.py`
- `tests/test_run_api_contract.py`

These cover:
- canonical artifact-driven report regeneration
- no `build_plan(...)` usage during regeneration
- stable API behavior for regenerated reports

### Template and Semantic Gates
Validated through:
- `tests/test_analysis_report_catalog.py`
- `tests/test_visualizations.py`
- `tests/test_analysis_views.py`

These cover:
- strict-mode template lookup failures
- fallback stability for unmapped protocols
- dual-series differential semantics
- discrimination-curve semantics
- tick-to-trial aggregation semantics

---

## Net State After V2.18.9

- analysis and report regeneration are more cleanly artifact-driven
- regenerated reports no longer depend on plan reconstruction
- protocol-template governance now supports strict CI/debug enforcement
- fallback template behavior remains stable in non-strict mode
- figure/view semantics are explicitly locked to finalized V2 runtime meaning

V2.18.9 therefore closes the main analysis/report canonicalization gap still remaining in the V2 closeout path.

## Validation Commands

Targeted gates exercised during implementation:
- `python -m pytest -q tests/test_report.py tests/test_verification_report.py tests/test_run_api_contract.py`
- `python -m pytest -q tests/test_analysis_report_catalog.py tests/test_visualizations.py tests/test_analysis_views.py`
