from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

_RUNTIME_OBSERVATION_SURFACES = [
    ROOT / "virtual_shaping_lab" / "vsl" / "runtime" / "observation_adapter.py",
    ROOT / "virtual_shaping_lab" / "vsl" / "runtime" / "learner_adapter.py",
    ROOT / "virtual_shaping_lab" / "vsl" / "rollout" / "harness.py",
]

_BANNED_IMPORT_TOKENS = [
    "virtual_shaping_lab.agents.representations.observation",
    "make_observation",
]


def test_v3_19_15_runtime_observation_surfaces_do_not_import_legacy_observation_helpers():
    violations: list[tuple[str, str]] = []
    for path in _RUNTIME_OBSERVATION_SURFACES:
        text = path.read_text(encoding="utf-8")
        import_lines = [
            line.strip()
            for line in text.splitlines()
            if re.match(r"^(from|import)\s+", line.strip())
        ]
        for token in _BANNED_IMPORT_TOKENS:
            if any(token in line for line in import_lines):
                violations.append((str(path.relative_to(ROOT)), token))
    assert not violations, f"Legacy observation import tokens found in runtime surfaces: {violations}"
