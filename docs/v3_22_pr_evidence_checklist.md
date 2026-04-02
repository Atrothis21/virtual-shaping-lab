# V3.22 PR Evidence Checklist

Use this checklist in PR descriptions for V3.22 measurement/runtime changes.

## Slice Completion Evidence
- [ ] Slice 1 end-to-end measurement integration matrix is present and passing
- [ ] Slice 2 replay/hash determinism hardening changes are present and passing
- [ ] Slice 3 closeout CI aggregation bucket is present and passing
- [ ] Slice 4 architecture note and evidence checklist docs are included
- [ ] Slice 5 plan closeout and summary artifacts are updated

## Ownership and Core Contract Evidence
- [ ] `tests/test_v3_measurement_contract_ownership.py` passed
- [ ] `tests/test_v3_measurement_grammar_spec.py` passed
- [ ] `tests/test_v3_measurement_validator.py` passed
- [ ] `tests/test_v3_measurement_registry.py` passed
- [ ] `tests/test_v3_measurement_presets.py` passed

## Executable Measurement Core Evidence
- [ ] `tests/test_v3_measurement_operators_base.py` passed
- [ ] `tests/test_v3_measurement_operators_analysis.py` passed
- [ ] `tests/test_v3_measurement_operators_visualization.py` passed
- [ ] `tests/test_v3_measurement_bundle_execution.py` passed
- [ ] `tests/test_v3_measurement_executable_instantiation.py` passed
- [ ] `tests/test_v3_measurement_golden.py` passed

## Runtime Seam and Boundary Evidence
- [ ] `tests/test_v3_runtime_measurement_adapter.py` passed
- [ ] `tests/test_v3_measurement_runtime_parity.py` passed
- [ ] `tests/test_v3_measurement_runtime_boundary_invariants.py` passed
- [ ] `tests/test_v3_measurement_runtime_loop_contract.py` passed
- [ ] measurement runtime execution remains post-run only (no protocol/agent-loop in-band measurement dispatch)

## Trace Promotion and Report Evidence
- [ ] `tests/test_v3_measurement_rollout_record_schema.py` passed
- [ ] `tests/test_v3_measurement_report_normalization.py` passed
- [ ] `tests/test_v3_measurement_trace_compatibility_bridges.py` passed
- [ ] Rollout records include `metadata.measurement_traces.{metrics,figures,summary,provenance}`
- [ ] Report normalized outputs include `measurement_metrics|measurement_figures|measurement_summary|measurement_provenance`

## Integration + Determinism Evidence
- [ ] `tests/test_v3_measurement_integration_matrix.py` passed
- [ ] `tests/test_v3_rollout_replay_harness.py -k "measurement or replay or hash"` passed
- [ ] Seeded replay hash identity remains stable for measurement-trace-inclusive runs
- [ ] measurement payload hash identity remains stable for equivalent seeded runs

## CI Bucket Evidence
- [ ] CI step `Run V3.22 measurement closeout gates` is present
- [ ] CI step `Run V3.22 measurement closeout gates` is green
- [ ] no regressions in dependent V3.22 buckets (`V3.22.0`, `V3.22.10`, `V3.22.15`)

## Architecture Assertions
- [ ] runtime measurement execution remains single-path through `RuntimeMeasurementAdapter` and `ReplayHarness.run_with_measurement(...)`
- [ ] measurement remains strictly post-run and read-only relative to protocol/agent runtime state
- [ ] canonical metadata and report trace surfaces remain stable
- [ ] no bypass of canonical measurement seam from rollout/report integration paths
- [ ] no non-deterministic payload ordering regressions affecting replay/hash identity

