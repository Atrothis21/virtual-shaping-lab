# V3 Ownership Split (Canonical)

This document is the canonical ownership boundary reference for V3.

## Ownership Table

| Layer | Owns | Does Not Own |
|---|---|---|
| Program | experiment sequencing and phase order | learner update math, transition kernels |
| Phase | local trial conditions/recipe declarations | environment stepping internals, learner math |
| Protocol | reusable phase mechanics templates | global sequencing policy, learner internals |
| Environment | executable contingencies, transition stepping, rewards, termination | representation transforms, learner slot logic |
| Representation | Phi/Ctx/Sim transforms and state encoding | reward logic, action policy |
| Learner | Pred/Err/Attn/Update/weights | sequencing, transition control |
| Policy | action selection over action space | transition/reward generation |
| Records + Analysis | rollout measurements/readouts/reporting | runtime transition ownership |

## Boundary Invariant (Normative)

- Program and Phase define what should happen; Environment defines what actually happens at runtime.
