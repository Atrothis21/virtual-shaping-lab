from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TRANSLATOR_JS = ROOT / "virtual_shaping_lab" / "ui" / "js" / "react" / "builder_draft_translator.js"
INDEX_APP = ROOT / "virtual_shaping_lab" / "ui" / "js" / "react" / "index_app.jsx"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_builder_translator_module_exports_draft_to_payload():
    text = _read(TRANSLATOR_JS)
    assert "window.VSLReact.builderDraftTranslator" in text
    assert "draft_to_payload" in text
    assert "settings" in text
    assert "report" in text


def test_builder_route_uses_translator_for_plan_submission():
    text = _read(INDEX_APP)
    assert "builderDraftTranslatorApi" in text
    assert "draft_to_payload(draftSeed)" in text
    assert "apiClient.postJson(\"plan\", translatedPayload)" in text
