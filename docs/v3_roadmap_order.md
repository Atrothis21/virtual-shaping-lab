# V3 Roadmap Order (Canonical)

This document is the canonical roadmap order and dependency map for V3.

## Execution Order

| Planning Label | Slice Name | Why It Sits Here |
|---|---|---|
| v3.0.x | documentation normalization + glossary + UTF-8 cleanup | eliminate notation/encoding ambiguity before engineering work |
| v3.1.x | typed semantic plan | stabilize ownership contracts early |
| v3.2.x | environment program compilation from phases/protocols | reframe phases as generators, not mechanisms |
| v3.3.x | first-class environment contract | make runtime semantics explicit |
| v3.4.x | universal action-space and policy unification | collapse architectural split between classical and operant |
| v3.4.5.x | explicit operator pipeline object | make noncommutative composition order first-class and test-enforced |
| v3.5.x | learner grammar + compatibility validator + preset registry | formalize model families after environment/policy contracts |
| v3.6.x | rollout engine + record schema finalization | lock runtime-analysis boundary early |
| v3.7.x | temporal representation + episode/horizon semantics | deepen time semantics after rollout contract is stable |
| v3.8.x | phenomenon registry + minimal operator bundles | scientific coverage after core runtime contracts settle |
| v3.8.5.x | layered UI abstraction and teaching surfaces | expose operators progressively while keeping behavior-first usability |
| v3.9.x | namespace/package reshaping + public API stabilization | physical package cleanup last |

## Cross-Slice Dependency Snapshot

| Slice | Depends On |
|---|---|
| v3.0.x | none |
| v3.1.x | v3.0.x |
| v3.2.x | v3.1.x |
| v3.3.x | v3.2.x |
| v3.4.x | v3.3.x |
| v3.4.5.x | v3.3.x, v3.4.x |
| v3.5.x | v3.3.x, v3.4.x, v3.4.5.x |
| v3.6.x | v3.1.x, v3.3.x |
| v3.7.x | v3.6.x |
| v3.8.x | v3.5.x, v3.6.x |
| v3.8.5.x | v3.5.x, v3.6.x, v3.8.x |
| v3.9.x | v3.1.x-v3.8.5.x stabilized |
