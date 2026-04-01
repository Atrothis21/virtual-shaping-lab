# V3.20.15 PR Evidence Checklist

Use this checklist in the V3.20.15 PR description.

## Slice Completion Evidence
- [ ] Slice 1 legality boundary files are present (`spec.py`, `validation.py`, `instantiate.py`)
- [ ] Slice 2 thin orchestrator surface is present (`composite.py`) and exported
- [ ] Slice 3 runtime harness executes through compositional-agent seam only
- [ ] Slice 4 guardrails + CI bucket are present and green
- [ ] Slice 5 architecture/evidence docs are included

## Guardrail Test Evidence
- [ ] `tests/test_v3_agent_composition_validator.py` passed
- [ ] `tests/test_v3_agent_execution.py` passed
- [ ] `tests/test_v3_agent_runtime_parity.py` passed
- [ ] `tests/test_v3_single_path_agent_execution.py` passed
- [ ] `tests/test_v3_agent_public_interface_contract.py` passed
- [ ] `tests/test_v3_agent_protocol_boundary_invariants.py` passed
- [ ] `tests/test_v3_agent_namespace_import_audit.py` passed
- [ ] `tests/test_v3_agent_namespace_hard_removal.py` passed

## Runtime/Report Coupling Evidence
- [ ] `tests/test_v3_runtime_observation_adapter.py` passed
- [ ] `tests/test_v3_runtime_learner_adapter.py` passed
- [ ] `tests/test_v3_runtime_policy_adapter.py` passed
- [ ] `tests/test_v3_rollout_record_schema.py` passed
- [ ] `tests/test_report.py -k "observation or learner or policy or agent"` passed

## CI Bucket Evidence
- [ ] CI step `Run V3.20.15 single-path compositional agent enforcement` is present
- [ ] CI step `Run V3.20.15 single-path compositional agent enforcement` is green
- [ ] No regressions in dependent V3.20.10 runtime seam bucket

## Architecture Closeout Assertions
- [ ] Runtime execution path uses `CompositionalAgent` as the single orchestration seam
- [ ] Agent keeps causal split:
  - pre-outcome: `observe/predict/act`
  - post-outcome: `learn/advance_internal_time`
- [ ] Protocol/outcome boundary does not carry internal learner update terms
- [ ] Closeout architecture note updated (`docs/v3_20_15_single_path_agent_architecture.md`)
