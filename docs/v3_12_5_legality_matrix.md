# V3.12.5 Legality Matrix Artifact

This document is the human-readable companion for:
- `docs/v3_12_5_legality_matrix.json`

The JSON artifact is CI-validated against:
- `virtual_shaping_lab/ui/contracts/operator_legality_engine.py`

## Rule Codes

- `LGL_E_SLOT_UNKNOWN_SELECTION`
  - kind: `slot_level`
  - selection must come from the registry universe for the slot
- `LGL_E_DELTA_REQUIRES_TRACE`
  - kind: `cross_slot`
  - `td_lambda_error` requires an eligibility/trace selection
- `LGL_E_POLICY_REQUIRES_ACTION_PREDICTOR`
  - kind: `cross_slot`
  - non-null policy requires action-capable predictor
- `LGL_E_CLASSICAL_POLICY_INCOMPATIBLE`
  - kind: `cross_slot`
  - `classical_contingency` is incompatible with action policies
- `LGL_E_ACTOR_CRITIC_TRIPLET`
  - kind: `cross_slot`
  - `actor_critic_update` requires compatible predictor+error pairing
- `LGL_E_MEASURE_REQUIRES_POLICY`
  - kind: `cross_slot`
  - `action_probabilities` measurement requires policy
- `LGL_E_MEASURE_REQUIRES_TRACE`
  - kind: `cross_slot`
  - `eligibility_curve` measurement requires trace mechanism
