# UI Known Limitations (Post V2.17.4)

## Purpose
Track known UI constraints that are accepted for the current release scope and should be revisited in follow-on slices.

## Current Limitations

1. Root-shell files are reduced but not minimal
- `index.html` and `index_app.jsx` were split into smaller route/component/service modules.
- Additional extraction is still possible for long-term maintainability (for example, deeper route-specific hooks/services).

2. Route scaffold tests are structure-focused
- Current UI tests are mostly scaffold/contract style.
- More behavior-driven browser-level tests can be added later for richer interaction validation.

3. Motion polish is intentionally restrained
- Motion system focuses on subtle status transitions and reduced-motion safety.
- More advanced animation patterns are intentionally deferred to avoid obscuring scientific workflow clarity.

4. Advanced/debug UX remains bounded
- Advanced/debug surfaces are present and intentionally low-prominence.
- Expanded operator tooling is deferred until core first-pass route stability is fully proven across future slices.

5. Catalog/help route remains lightweight
- Catalog/help currently emphasizes runtime visibility and version checks.
- Richer documentation navigation/search in-app is deferred.

## Exit Guidance for Removal

Remove or reduce these limitations when:
- route-level services/selectors are fully isolated with stable interfaces
- browser-level integration tests cover major failure and recovery workflows
- UI performance and accessibility budgets are measured and enforced in CI
- advanced/debug operator needs are formalized beyond current bounded scope
