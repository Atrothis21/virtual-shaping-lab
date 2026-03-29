# V3.18.15 PR Evidence Checklist

Use this checklist in the V3.18.15 PR description.

## Deletion/Refactor Evidence
- [ ] Legacy learner path inventory reviewed (`docs/v3_18_15_legacy_learner_path_inventory.md`)
- [ ] Duplicate execution branches removed or explicitly bridged with expiry notes
- [ ] Deprecated learner surfaces removed (or justified as deferred with owner/date)
- [ ] No tracked Python cache artifacts committed

## Guardrail Evidence
- [ ] `tests/test_v3_single_path_execution.py` passed
- [ ] `tests/test_v3_18_15_single_path_guardrails.py` passed
- [ ] `tests/test_v3_namespace_import_audit.py` passed
- [ ] `tests/test_v3_namespace_hard_removal.py` passed

## Runtime/Behavior Evidence
- [ ] `tests/test_v3_runtime_learner_adapter.py` passed
- [ ] `tests/test_v3_learner_runtime_parity.py` passed
- [ ] `tests/test_v3_learner_numeric_golden.py` passed

## API Metadata Identity Evidence
- [ ] `tests/test_run_api_contract.py -k "payload_mode_identity or basis_compile_identity or measurement_provenance_identity"` passed

## CI Bucket Evidence
- [ ] CI step `Run V3.18.15 single-path enforcement` is present and green
- [ ] No failures in dependent V3 learner/runtime buckets after cleanup

## Closeout Assertions
- [ ] Runtime has one learner execution path (`RuntimeLearnerAdapter -> LearnerBundle`)
- [ ] No update-only learner fallback remains in runtime path
- [ ] Architecture note updated (`docs/v3_18_15_single_path_learner_architecture.md`)
