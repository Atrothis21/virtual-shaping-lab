# V3.19.15 Legacy Observation Path Inventory

## Purpose
Inventory observation/feature construction surfaces outside the canonical V3 runtime observation seam:

- canonical target path:
  - `RuntimeObservationAdapter -> ObservationBundle.step(...)`

This document classifies each path as:
- `keep`
- `bridge`
- `delete-now`
- `delete-later`

---

## Canonical Keep

- `virtual_shaping_lab/vsl/runtime/observation_adapter.py`
  - owner: V3 runtime
  - reason: canonical runtime observation seam

- `virtual_shaping_lab/vsl/rollout/harness.py`
  - owner: V3 rollout runtime
  - reason: environment path now calls runtime observation adapter and forwards finalized observation features to learner adapter

- `virtual_shaping_lab/vsl/agent/observation/bundle.py`
  - owner: V3 observation core
  - reason: canonical executable observation pipeline (`represent -> contextualize -> generalize -> finalize`)

- `virtual_shaping_lab/vsl/records/adapters/rollout_records.py`
  - owner: V3 record boundary
  - reason: canonical promotion of observation traces to record metadata

- `virtual_shaping_lab/analysis/report/report.py`
  - owner: analysis/report boundary
  - reason: canonical report normalization of promoted observation traces

---

## Bridge (Temporary Compatibility)

- `virtual_shaping_lab/vsl/runtime/learner_adapter.py::_coerce_features_from_stimulus(...)`
  - owner: V3 runtime/learner boundary
  - reason: fallback for legacy callers that do not yet provide observation-feature inputs
  - bridge rule: allowed only while non-observation-seam callers exist
  - expiry target: remove after Slice 2 migration confirms no runtime caller relies on raw-stimulus feature coercion

- `virtual_shaping_lab/experiment/trial_executor.py`
  - owner: legacy/v2.1 runnable-unit path
  - reason: step-level agent observation still constructed as dataclass `Observation` objects on runnable-unit execution path
  - bridge rule: retain while runnable-unit protocol/phase surfaces remain active
  - expiry target: V3.19.15+ cleanup after single-path runtime enforcement is complete

- `virtual_shaping_lab/experiment/runner.py` (`_run_runnable_unit(...)`)
  - owner: legacy/v2.1 runnable-unit path
  - reason: delegates legacy observation-bearing `StepResult` records
  - bridge rule: retain until runnable-unit observation path migration/removal is complete
  - expiry target: aligned with trial-executor runnable-unit cleanup

---

## Delete-Now Candidates

None marked safe for immediate deletion in Slice 1 without behavior migration guardrails.

Rationale:
- phase-level legacy observation constructors are broad and currently tied to runnable-unit compatibility contracts; they should be removed in Slice 2 under explicit runtime/CI guardrails rather than deleted opportunistically.

---

## Delete-Later Candidates (Primary Slice 2/3 Targets)

Direct phase-level observation constructors via:
- `from virtual_shaping_lab.agents.representations.observation import make_observation`

Files:
- `virtual_shaping_lab/experiment/phases/acquisition.py`
- `virtual_shaping_lab/experiment/phases/compound_acquisition.py`
- `virtual_shaping_lab/experiment/phases/compound_nonreinforcement.py`
- `virtual_shaping_lab/experiment/phases/concurrent_schedule.py`
- `virtual_shaping_lab/experiment/phases/criterion_shift.py`
- `virtual_shaping_lab/experiment/phases/differential_acquisition.py`
- `virtual_shaping_lab/experiment/phases/nonreinforcement.py`
- `virtual_shaping_lab/experiment/phases/operant_acquisition.py`
- `virtual_shaping_lab/experiment/phases/probe.py`

Shared helper surface:
- `virtual_shaping_lab/agents/representations/observation.py` (`make_observation(...)`)

Delete-later policy:
- remove only after runtime paths are fully constrained to the canonical observation adapter seam and corresponding compatibility tests are either migrated or explicitly retired.

---

## Ownership Notes

- V3 runtime ownership:
  - canonical observation seam and single-path enforcement
- Legacy experiment ownership:
  - runnable-unit and phase-level observation constructors pending migration/removal
- Report/record ownership:
  - observation trace persistence and projection contracts

---

## Immediate Follow-On for Slice 2

- remove duplicate runtime/phase observation execution branches that bypass `RuntimeObservationAdapter`
- keep only explicitly documented temporary bridges with expiry notes
- add CI drift checks to block reintroduction of direct feature/observation construction in runtime seam files
