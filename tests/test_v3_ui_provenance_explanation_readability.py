from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
JS_DIR = ROOT / "virtual_shaping_lab" / "ui" / "js" / "react"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_tuple_flow_declares_provenance_readability_interpretation_layer():
    src = _read(JS_DIR / "tuple_authoring_flow.jsx")
    assert "deriveReadableProvenanceFactors(" in src
    assert "required_operators" in src
    assert "task_implementation_id" in src
    assert "forbidden_slots" in src


def test_provenance_readability_layer_emits_human_readable_sentences():
    src = _read(JS_DIR / "tuple_authoring_flow.jsx")
    assert "Required operator slots shape this behavior:" in src
    assert "Task implementation drives protocol behavior:" in src
    assert "Arrangement constraints forbid slots:" in src
