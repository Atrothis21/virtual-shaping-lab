from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOCS_DIR = ROOT / "docs"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_behavioral_compatibility_and_smart_preset_doc_declares_contract_statuses_and_endpoints():
    src = _read(DOCS_DIR / "v3_behavioral_compatibility_and_smart_presets.md")
    assert "`success`" in src
    assert "`partial`" in src
    assert "`structurally_invalid`" in src
    assert "`behaviorally_unsupported`" in src
    assert "`novel`" in src
    assert "POST /catalog/tuple-authoring/compatibility" in src
    assert "GET /catalog/smart-presets" in src
    assert "POST /catalog/smart-presets/{smart_preset_id}/project" in src


def test_smart_preset_migration_notes_include_core_label_mappings_and_tuple_boundary():
    src = _read(DOCS_DIR / "v3_16_0_smart_preset_migration_notes.md")
    assert "`acquisition` -> `classical_acquisition`" in src
    assert "`extinction` -> `classical_extinction`" in src
    assert "`differential_acquisition` -> `classical_differential_acquisition`" in src
    assert "`operant_conditioning` -> `operant_acquisition`" in src
    assert "`arrangement`" in src
    assert "`task`" in src
    assert "`agent`" in src
    assert "`edits`" in src
