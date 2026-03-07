from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INDEX_APP = ROOT / "virtual_shaping_lab" / "ui" / "js" / "react" / "index_app.jsx"
INDEX_HTML = ROOT / "virtual_shaping_lab" / "ui" / "index.html"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_builder_controls_bind_to_draft_and_emit_draft_edited_event():
    text = _read(INDEX_APP)
    assert "onDraftEdited" in text
    assert "updateDraftPatch" in text
    assert "editBuilderDraft" in text
    assert "type: stateApi.UI_EVENTS.DRAFT_EDITED" in text
    assert "payload: { draft: nextDraft }" in text
    assert "run_mode_hint" in text
    assert "template_key" in text
    assert "protocol_key" in text
    assert "expected_signals" in text


def test_builder_route_surfaces_validation_and_readiness_state():
    text = _read(INDEX_APP)
    assert "Draft Readiness:" in text
    assert "Validation Errors:" in text
    assert "validation_state:" in text
    assert "is_ready:" in text


def test_builder_control_and_validation_styles_exist():
    text = _read(INDEX_HTML)
    assert ".builder-control" in text
    assert ".builder-control input" in text
    assert ".builder-control select" in text
    assert ".builder-validation-panel" in text
