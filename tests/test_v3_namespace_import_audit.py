from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PKG = ROOT / "virtual_shaping_lab"

LEGACY_IMPORT_TOKENS = [
    "virtual_shaping_lab.vsl.operator",
    "virtual_shaping_lab.vsl.rollout.records",
    "virtual_shaping_lab.vsl.rollout.replay",
    "virtual_shaping_lab.vsl.environment.harness",
    "virtual_shaping_lab.vsl.environment.episode",
    "virtual_shaping_lab.vsl.environment.trial_state",
    "virtual_shaping_lab.vsl.spec.binding",
    "virtual_shaping_lab.vsl.spec.models",
    "virtual_shaping_lab.vsl.agent.learning.boundary",
    "virtual_shaping_lab.vsl.agent.learning.validator",
    "virtual_shaping_lab.vsl.agent.representation.temporal",
    "virtual_shaping_lab.vsl.records.types",
    "virtual_shaping_lab.vsl.registry.phenomenon_registry",
]


def test_v3_slice4_import_audit_has_no_internal_legacy_namespace_imports():
    violations: list[tuple[str, str]] = []
    for path in PKG.rglob("*.py"):
        text = path.read_text(encoding="utf-8")
        import_lines = [
            line.strip()
            for line in text.splitlines()
            if re.match(r"^(from|import)\s+", line.strip())
        ]
        for token in LEGACY_IMPORT_TOKENS:
            if any(token in line for line in import_lines):
                violations.append((str(path.relative_to(ROOT)), token))
    assert not violations, f"Legacy namespace import violations: {violations}"
