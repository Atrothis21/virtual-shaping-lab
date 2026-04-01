from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

_RUNTIME_PROTOCOL_SURFACES = [
    ROOT / "virtual_shaping_lab" / "vsl" / "runtime" / "protocol_adapter.py",
    ROOT / "virtual_shaping_lab" / "vsl" / "rollout" / "harness.py",
]

_BANNED_IMPORT_TOKENS = [
    "experiment.phases.",
    "experiment.factories.phase_factory",
    "experiment.protocols",
]


def test_v3_21_15_runtime_protocol_surfaces_do_not_import_legacy_protocol_paths():
    violations: list[tuple[str, str]] = []
    for path in _RUNTIME_PROTOCOL_SURFACES:
        text = path.read_text(encoding="utf-8")
        import_lines = [line.strip() for line in text.splitlines() if re.match(r"^(from|import)\s+", line.strip())]
        for token in _BANNED_IMPORT_TOKENS:
            if any(token in line for line in import_lines):
                violations.append((str(path.relative_to(ROOT)), token))
    assert not violations, f"Legacy protocol namespace import violations: {violations}"
