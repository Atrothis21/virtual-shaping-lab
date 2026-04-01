# V3.21 PR Evidence Checklist

Use this checklist in PR descriptions for V3.21 protocol/runtime changes.

## Slice Completion Evidence
- [ ] Slice 1 end-to-end protocol integration matrix is present and passing
- [ ] Slice 2 replay/hash determinism hardening changes are present and passing
- [ ] Slice 3 closeout CI aggregation bucket is present and passing
- [ ] Slice 4 architecture note and evidence checklist docs are included
- [ ] Slice 5 plan closeout and summary artifacts are updated

## Ownership and Core Contract Evidence
- [ ] `tests/test_v3_protocol_contract_ownership.py` passed
- [ ] `tests/test_v3_protocol_bundle_execution.py` passed
- [ ] `tests/test_v3_protocol_executable_instantiation.py` passed
- [ ] `tests/test_v3_protocol_golden.py` passed

## Runtime Seam and Boundary Evidence
- [ ] `tests/test_v3_runtime_protocol_adapter.py` passed
- [ ] `tests/test_v3_protocol_runtime_parity.py` passed
- [ ] `tests/test_v3_agent_protocol_loop_contract.py` passed
- [ ] `tests/test_v3_agent_protocol_boundary_invariants.py` passed

## Trace Promotion and Report Evidence
- [ ] `tests/test_v3_rollout_record_schema.py -k protocol` passed
- [ ] `tests/test_report.py -k protocol` passed
- [ ] Rollout records include `metadata.protocol_traces.*`
- [ ] Report normalized outputs include protocol fields (`protocol_emission`, `protocol_consequence`, `protocol_advance`, `protocol_stop`, `protocol_timing`, `protocol_provenance`)

## Single-Path and Namespace Guard Evidence
- [ ] `tests/test_v3_single_path_protocol_execution.py` passed
- [ ] `tests/test_v3_protocol_namespace_import_audit.py` passed
- [ ] `tests/test_v3_protocol_namespace_hard_removal.py` passed

## Integration + Determinism Evidence
- [ ] `tests/test_v3_protocol_integration_matrix.py` passed
- [ ] `tests/test_v3_rollout_replay_harness.py -k "protocol or replay or hash"` passed
- [ ] Seeded replay hash identity remains stable for protocol-trace-inclusive runs

## CI Bucket Evidence
- [ ] CI step `Run V3.21 protocol closeout gates` is present
- [ ] CI step `Run V3.21 protocol closeout gates` is green
- [ ] No regressions in dependent V3.21 buckets (`V3.21.10`, `V3.21.15`)

## Architecture Assertions
- [ ] Runtime protocol execution remains single-path through `RuntimeProtocolAdapter.emit/resolve`
- [ ] Causal split remains explicit:
  - protocol/environment: emission -> consequence -> advance -> stop
  - agent: observe -> predict -> act -> learn -> advance_internal_time
- [ ] Protocol boundary objects remain narrow/typed (`TaskInput`, `Action`, `Outcome`, `TrialRecord`)
- [ ] Protocol runtime surfaces do not compute learner internals
- [ ] No agent mutation of protocol timeline/state outside canonical boundary
