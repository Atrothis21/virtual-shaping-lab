# V3.20.10 Summary - Runtime Policy Seam and Policy Trace Promotion

## Overview
V3.20.10 introduces a canonical runtime policy adapter seam, routes runtime action selection through executable policy contracts, enforces pre-outcome vs post-outcome loop ordering, and promotes policy traces into rollout record/report normalization.

Primary outcomes:
- added canonical runtime policy seam (`RuntimePolicyAdapter`) and builder API
- routed runtime harness policy selection through adapter-bound executable policy path
- enforced causal loop ordering: pre-outcome policy selection, post-outcome learner update
- added runtime parity/ownership tests for policy seam integration
- promoted policy traces into rollout record metadata and report normalization surfaces
- added blocking CI bucket for runtime policy seam and trace contracts

This slice closes the V3.20.10 milestone for runtime policy seam integration and policy-trace contract promotion.

---

## Slice 1 - Runtime Policy Adapter

### Objective
Add one canonical runtime policy seam and normalize runtime available-actions payloads into policy input transport.

### Implemented
Added:
- `virtual_shaping_lab/vsl/runtime/policy_adapter.py`

Updated:
- `virtual_shaping_lab/vsl/runtime/__init__.py`
- `virtual_shaping_lab/vsl/__init__.py`
- `V3.20.10_plan.md`

Changes:
- added runtime policy adapter APIs:
  - `RuntimePolicyAdapter`
  - `build_runtime_policy_adapter(...)`
- added runtime normalization helpers for:
  - available actions
  - task input coercion
  - observation output coercion
- enforced policy execution through executable policy presets via `build_policy_input(...)` boundary

---

## Slice 2 - Harness Integration and Ordering

### Objective
Route runtime action selection through policy seam and enforce explicit pre-outcome vs post-outcome ordering.

### Implemented
Updated:
- `virtual_shaping_lab/vsl/rollout/harness.py`
- `V3.20.10_plan.md`

Changes:
- added policy seam injection to environment harness:
  - `CompiledProgramTestEnvironment(..., policy_adapter=...)`
- enforced runtime loop order:
  - pre-outcome: observe -> policy select
  - post-outcome: consequence -> learner update
- preserved explicit caller action override when provided by `RolloutHarness.run(..., action=...)`
- added policy metadata surface in environment step emission:
  - action
  - available actions
  - action scores/probabilities
  - policy metadata

---

## Slice 3 - Runtime Parity and Ownership Tests

### Objective
Add parity and ownership tests to ensure runtime policy seam is canonical and non-bypassable.

### Implemented
Added:
- `tests/test_v3_runtime_policy_adapter.py`
- `tests/test_v3_policy_runtime_parity.py`
- `tests/test_v3_agent_protocol_loop_contract.py`

Updated:
- `V3.20.10_plan.md`

Changes:
- added runtime adapter construction/normalization coverage
- added parity checks between runtime adapter output and direct executable policy output
- added loop ownership/causal-order guards for observe -> policy -> learner sequencing
- fixed loop-order expectation for terminal one-step fixture path in protocol loop contract test

---

## Slice 4 - Record/Report Policy Trace Promotion

### Objective
Promote policy traces into rollout records and report normalization.

### Implemented
Updated:
- `virtual_shaping_lab/vsl/records/adapters/rollout_records.py`
- `virtual_shaping_lab/analysis/report/report.py`
- `tests/test_v3_rollout_record_schema.py`
- `tests/test_report.py`
- `V3.20.10_plan.md`

Changes:
- added `metadata.policy_traces` promotion in rollout record adapter:
  - action
  - available actions
  - action scores/probabilities
  - provenance metadata
- added policy normalization fields in report record normalization:
  - `policy_action`
  - `policy_available_actions`
  - `policy_action_scores`
  - `policy_action_probabilities`
  - `policy_provenance`
- backfilled `action` and `policy_state` from policy traces when absent

---

## Slice 5 - CI Runtime Bucket and Gate Tightening

### Objective
Add blocking CI bucket for runtime policy seam/parity/trace contracts.

### Implemented
Updated:
- `.github/workflows/ci.yml`
- `V3.20.10_plan.md`
- `tests/test_v3_agent_protocol_loop_contract.py`

Changes:
- added blocking CI step:
  - `Run V3.20.10 runtime policy seam and traces`
- bucket covers:
  - runtime policy adapter + parity + loop contract tests
  - runtime observation/learner seam companion checks
  - policy-focused rollout record/report normalization checks
- corrected protocol loop event-order assertion for one-step terminal fixture

---

## Closeout Impact

After V3.20.10:
- runtime action selection is adapter-bound through canonical executable policy path
- runtime loop ordering explicitly separates pre-outcome policy behavior from post-outcome learner updates
- policy traces are promoted into record/report surfaces with stable normalized fields
- CI blocks policy seam bypass, parity drift, and policy-trace regression paths

V3.20.10 therefore completes runtime policy seam and trace-promotion hardening for the V3.20 line.

---

## Validation

### Slice and Contract Gates
Validated via:
- `tests/test_v3_runtime_policy_adapter.py`
- `tests/test_v3_policy_runtime_parity.py`
- `tests/test_v3_agent_protocol_loop_contract.py`
- `tests/test_v3_runtime_observation_adapter.py`
- `tests/test_v3_runtime_learner_adapter.py`
- `tests/test_v3_rollout_record_schema.py -k policy`
- `tests/test_report.py -k policy`

### CI-Facing Contract Checks
Validated by assertions that:
- runtime policy dispatch remains seam-bound and canonical
- runtime adapter output parity remains aligned with executable policy operators
- causal loop ordering prevents hidden learn-inside-pre-outcome flow
- record/report policy trace fields remain present and stable

---

## Net State After V3.20.10

- canonical runtime policy seam is implemented and exported
- runtime harness routes policy selection through adapter-bound executable policy path
- policy traces are integrated into rollout and report normalization surfaces
- blocking CI bucket enforces runtime seam, parity, and trace contracts

V3.20.10 establishes the runtime-ready baseline for downstream V3.20.x policy/loop simplification and closeout.

## Validation Commands

Targeted gates for local/CI execution:
- `python -m pytest -q tests/test_v3_runtime_policy_adapter.py tests/test_v3_policy_runtime_parity.py tests/test_v3_agent_protocol_loop_contract.py`
- `python -m pytest -q tests/test_v3_runtime_observation_adapter.py tests/test_v3_runtime_learner_adapter.py`
- `python -m pytest -q tests/test_v3_rollout_record_schema.py -k policy`
- `python -m pytest -q tests/test_report.py -k policy`
