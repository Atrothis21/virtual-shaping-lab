from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GUARDS = ROOT / "virtual_shaping_lab" / "ui" / "js" / "react" / "builder_submission_guards.js"
INDEX_APP = ROOT / "virtual_shaping_lab" / "ui" / "js" / "react" / "index_app.jsx"
PLAN_WORKFLOW = ROOT / "virtual_shaping_lab" / "ui" / "js" / "react" / "plan_workflow_service.js"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_builder_submission_guards_export_boundary_checks():
    text = _read(GUARDS)
    assert "VSLReact.builderSubmissionGuards" in text
    assert "assertBuilderDraftForTranslation" in text
    assert "assertTranslatedBuilderPayload" in text
    assert "Builder route rejected direct payload-shaped draft input." in text
    assert "Translator output missing required settings/report payload sections." in text
    assert "Translator boundary violation: draft-only fields leaked into submission payload." in text


def test_builder_plan_resolve_path_uses_submission_guards():
    text = _read(INDEX_APP) + _read(PLAN_WORKFLOW)
    assert "builderSubmissionGuardsApi" in text
    assert "assertBuilderDraftForTranslation" in text
    assert "assertTranslatedBuilderPayload" in text
    assert "Builder submission guard blocked payload." in text
    assert "apiClient.postJson(\"plan\", translatedPayload)" in text
    assert "apiClient.postJson(\"plan\", draftSeed)" not in text
