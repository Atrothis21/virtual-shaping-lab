Partially complete. `V_3_changes.md` now correctly elevates both `TrialState` and `OperatorPipeline` to first-class required objects.

However, to guarantee strict correspondence with the formal algebra, both still need tighter mathematical specification.

## Summary

- `TrialState`: good direction, not fully pinned down.
- `OperatorPipeline`: good direction, but stage order and stage contracts must remain explicit and enforceable.

## 1. TrialState Audit

### What the formal algebra requires

Carrier state:

- `Xi_t = (s_t, x_t, z_t, w_t, a_t, u_t, y_t, m_t)`

Where:

- `s`: raw environmental situation/presented stimuli
- `x`: encoded representation
- `z`: context/trace/memory state
- `w`: learned parameters
- `a`: attention/associability state
- `u`: chosen action
- `y`: realized outcome/reinforcement
- `m`: metadata/schedule/counter state

### Current state in `V_3_changes.md`

- Requires `TrialState` as first-class typed object.
- Requires runtime to consume/emit typed `TrialState`.

### Remaining requirements

1. Canonical field map must be explicitly normative.
2. Persistent vs derived boundary must be explicit.
3. Classical compatibility for action field must be explicit.

Recommended constraints:

- `TrialState.u` always present.
- Classical tasks use null/singleton action values.
- Prediction/error remain derived outputs unless explicitly cached.

## 2. OperatorPipeline Audit

### What the formal algebra requires

Composition is typed and noncommutative.

For generic trial semantics, order should be:

- `Phi -> C -> G -> E -> P -> Policy -> Env -> Err -> A -> Update -> Measure`

### Current state in `V_3_changes.md`

- Requires `OperatorPipeline` and `OperatorStage`.
- Requires declaration-based execution and noncommutativity tests.

### Remaining requirements

1. Default order must match formal trial semantics.
2. `Err` must support post-`Env` lookahead dependency for TD-style learners.
3. Every stage must declare typed input/output contracts over `TrialState`.

Recommended stage-contract examples:

- `Phi`: sets/updates representation fields
- `Policy`: sets action field `u`
- `Env`: sets next situation/outcome/metadata
- `Err`: sets error terms (possibly consuming next prediction targets)
- `Update`: applies parameter update effects

## 3. Combined Assessment

- `TrialState`: near complete once canonical field and persistence rules are explicit.
- `OperatorPipeline`: near complete once order and stage contracts are explicit and enforced.

## 4. Minimal Required Fixes

To fully align architecture with the formal algebra:

1. Add normative `TrialState` field map.
2. Add persistent-vs-derived rule.
3. Ensure action field is always present with classical null/singleton compatibility.
4. Lock default pipeline order to formal runtime semantics.
5. Add explicit TD/lookahead rule for `Err`.
6. Require typed stage input/output contracts for all operator stages.

## Bottom Line

`V_3_changes.md` now has the right structural components.

To reach full mathematical realization (not only software architecture alignment), the remaining work is contract tightening:

- canonical carrier-state definition
- strict stage-order semantics
- explicit typed morphism contracts for pipeline stages
