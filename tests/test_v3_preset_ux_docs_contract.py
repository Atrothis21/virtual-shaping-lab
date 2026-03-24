from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOCS_DIR = ROOT / "docs"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_v3_17_preset_ux_cutover_doc_declares_route_strategy_and_expected_outcome_model():
    src = _read(DOCS_DIR / "v3_17_0_preset_ux_cutover.md")
    assert "Catalog IA and Route Strategy" in src
    assert "Expected Outcome Interaction Model" in src
    assert "`success`" in src
    assert "`partial`" in src
    assert "`behaviorally_unsupported`" in src
    assert "`novel`" in src
    assert "`structurally_invalid` is not a compatibility badge state" in src
    assert "blocked only for composition/legality failures" in src


def test_v3_17_preset_ux_cutover_doc_declares_api_surfaces_and_identity_parity():
    src = _read(DOCS_DIR / "v3_17_0_preset_ux_cutover.md")
    assert "GET /catalog/preset-ux" in src
    assert "GET /catalog/preset-route-migration" in src
    assert "GET /catalog/tuple-authoring" in src
    assert "POST /catalog/tuple-authoring/compatibility" in src
    assert "GET /catalog/smart-presets" in src
    assert "POST /catalog/smart-presets/{smart_preset_id}/project" in src
    assert "`tuple_authoring_identity`" in src
    assert "`preset_ux_identity`" in src
    assert "`artifact_identity.json`" in src


def test_v3_17_preset_ux_cutover_doc_includes_migration_playbook_and_checklist():
    src = _read(DOCS_DIR / "v3_17_0_preset_ux_cutover.md")
    assert "Migration Playbook for Remaining Legacy Routes" in src
    assert "Post-Cutover Checklist for New Presets" in src
    assert "route migration contract updated and tested" in src
    assert "Run V3 preset UX cutover" in src
