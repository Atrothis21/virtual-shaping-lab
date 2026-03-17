# V2.18.8 Summary - UI/API Canonical Contract Cleanup

## Overview
V2.18.8 aligns product-facing UI/API surfaces with the final canonical V2 payload and ownership model.

Primary outcomes:
- UI builder translation now emits canonical payloads directly
- builder-generated phases now carry explicit canonical `trials`
- UI translation no longer depends on a legacy intermediate payload shape
- API report payload construction now uses `plan.canonical_payload` directly
- results UI now reads canonical experiment structure instead of legacy flat fields

This slice closes one of the last V2 transitional seams where user-facing tooling still worked through migration-era payload assumptions even though runtime had already moved to canonical-only semantics.

---

## Builder Canonicalization

### Direct Canonical Emission
The builder translator now emits canonical payloads directly rather than:

- constructing a legacy-shaped experiment object
- converting that object back into canonical form afterward

The translated payload now writes the canonical ownership map directly:

- `experiment.program.phases`
- `experiment.agent.representation`
- `experiment.agent.learning`
- `experiment.agent.policy`
- `experiment.runtime`

This removes a migration-era round-trip from the UI contract path.

### Canonical Phase Structure
Builder-generated phases now include:

- `name`
- `protocol`
- `stimuli`
- `params`
- `trials`

This means the UI builder no longer emits phase entries that rely on runtime compatibility backfill for `n_trials`.

### Representation Normalization
The builder translator still supports simple representation keys in drafts, but now normalizes them directly into canonical representation objects with inferred `params.stimuli` before emitting the payload.

Net effect:
- the builder remains simple at the draft layer
- the emitted payload is canonical-first and runtime-ready

---

## API and Consumer Cleanup

### Report Payload Construction from Canonical Plan State
`RunService._build_report_payload_from_plan(...)` now builds report payloads from:

- `plan.canonical_payload`

instead of reconstructing canonical shape from flattened `plan.settings`.

This is the key architectural cleanup in Slice 2:
- report generation now consumes first-class canonical plan state rather than compatibility leftovers

### Canonical Results Consumer
The results view now reads:

- `experiment.program.phases`
- `experiment.agent.*`
- `experiment.runtime`

instead of legacy flat fields such as:

- `experiment.protocol`
- `experiment.params`
- `experiment.phases`
- `experiment.learner`
- `experiment.agent` as a flat string-only contract

This keeps the shipped UI aligned with the actual persisted payload artifacts.

### Envelope Stability Preserved
The external API envelope remains stable:

- run/status/report top-level response keys are unchanged
- contract snapshots remain valid

The change is therefore internal/product-structure cleanup, not a breaking external API redesign.

---

## Canonical Ownership Alignment

### UI Contract
After V2.18.8, builder translation is no longer a place where canonical ownership is temporarily flattened back into:

- legacy learner fields
- legacy protocol/params top-level experiment fields
- legacy representation/policy ownership placement

### API Contract
After V2.18.8, API-internal report payload construction is no longer a place where canonical plan state is reconstructed indirectly from compatibility settings.

Net effect:
- both UI emission and API-side report payload construction now honor the same ownership grammar as runtime

This improves coherence across:
- builder
- runtime
- persisted artifacts
- results UI

---

## Validation

### Builder Translation Gates
Validated through:
- `tests/test_ui_builder_draft_translation.py`
- `tests/test_ui_builder_draft_contracts.py`
- `tests/test_full_payloads.py`

These cover:
- canonical builder translation shape
- explicit phase `trials`
- translation validity under classical and operant builder drafts
- compatibility with the current full-payload integration surface

### API and Consumer Gates
Validated through:
- `tests/test_run_api_contract.py`
- `tests/test_api_contract_snapshots.py`
- `tests/test_ui_teaching_contract.py`

These cover:
- stable API run/status/report envelopes
- canonical-first report payload construction compatibility
- unchanged teaching/preset UI contracts

---

## Net State After V2.18.8

- UI builder payload emission is canonical-first
- builder-generated phases no longer rely on legacy runtime phase-shape compatibility
- API report payload construction now uses canonical plan state directly
- results UI now reads the same canonical payload shape that runtime persists
- user-facing surfaces are more closely aligned with the final V2 architecture without changing the external API envelope

V2.18.8 therefore closes the main UI/API canonical-contract gap still remaining in the V2 closeout path.

## Validation Commands

Targeted gates exercised during implementation:
- `python -m pytest -q tests/test_ui_builder_draft_translation.py tests/test_ui_builder_draft_contracts.py tests/test_full_payloads.py`
- `python -m pytest -q tests/test_run_api_contract.py tests/test_api_contract_snapshots.py tests/test_ui_teaching_contract.py`
