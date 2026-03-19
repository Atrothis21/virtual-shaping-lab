# V3.0.0 Plan - Documentation Hardening and Language Freeze

## Objective
Normalize V3 planning/contract docs so all downstream implementation slices share one stable glossary, ownership map, and roadmap order.

## Entry Criteria
- V2 closeout docs are stable for this release line.
- Architecture owner approves canonical glossary terms once.

## Entry Points
- `V_3_changes.md`
- `docs/v3_glossary.md` (new)
- `docs/v3_roadmap_order.md` (new)
- `docs/v3_ownership_split.md` (new)

## Source of Truth
- Glossary: `docs/v3_glossary.md`

## Commit-Sized Slices
### Slice 1 - Canonical Glossary Doc
- Create `docs/v3_glossary.md`.
- Move glossary table from planning doc into canonical reference doc.

### Slice 2 - Ownership and Roadmap Docs
- Create `docs/v3_ownership_split.md` and `docs/v3_roadmap_order.md`.
- Cross-link these docs from `V_3_changes.md`.

### Slice 3 - UTF-8 and Mojibake Cleanup
- Normalize all `docs/v3_*.md` files to UTF-8.
- Remove mojibake/corrupted symbols across the V3 doc set.

### Slice 4 - Reference Wiring Pass
- Ensure each V3 slice references the canonical glossary doc.
- Add a short “source-of-truth” note in each planning artifact.

## Testing / CI Updates
- Add UTF-8 lint check for `docs/v3_*.md`.
- Add mojibake token grep check across `docs/v3_*.md` (must return zero matches).

## Exit Criteria
- All V3 docs pass UTF-8 lint.
- Mojibake check is clean.
- Single canonical glossary exists and is referenced by all slices.

## Migration Impact
- Documentation-only; no runtime behavior changes.
