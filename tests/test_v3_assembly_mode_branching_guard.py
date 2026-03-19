from __future__ import annotations

import ast
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ASSEMBLY_MODULE = ROOT / "virtual_shaping_lab" / "experiment" / "assemble.py"
FORBIDDEN_MODE_LITERALS = {"classical_agent", "operant_agent", "classical", "operant"}


def _string_literals(node: ast.AST) -> set[str]:
    values: set[str] = set()
    for child in ast.walk(node):
        if isinstance(child, ast.Constant) and isinstance(child.value, str):
            values.add(child.value)
    return values


def test_no_mode_branching_in_assembly():
    tree = ast.parse(ASSEMBLY_MODULE.read_text(encoding="utf-8"), filename=str(ASSEMBLY_MODULE))

    violations: list[tuple[int, str, list[str]]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.If):
            hits = sorted(FORBIDDEN_MODE_LITERALS.intersection(_string_literals(node.test)))
            if hits:
                violations.append((node.lineno, "if", hits))
        elif isinstance(node, ast.IfExp):
            hits = sorted(FORBIDDEN_MODE_LITERALS.intersection(_string_literals(node.test)))
            if hits:
                violations.append((node.lineno, "ifexp", hits))
        elif isinstance(node, ast.Match):
            subject_hits = sorted(FORBIDDEN_MODE_LITERALS.intersection(_string_literals(node.subject)))
            pattern_hits = sorted(
                {
                    hit
                    for case in node.cases
                    for hit in FORBIDDEN_MODE_LITERALS.intersection(_string_literals(case.pattern))
                }
            )
            hits = sorted(set(subject_hits + pattern_hits))
            if hits:
                violations.append((node.lineno, "match", hits))

    assert not violations, (
        "Assembly mode-branching violations detected in composition root "
        f"{ASSEMBLY_MODULE.relative_to(ROOT)}: {violations}"
    )

