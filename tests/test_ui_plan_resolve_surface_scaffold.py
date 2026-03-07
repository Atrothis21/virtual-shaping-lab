from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INDEX_APP = ROOT / "virtual_shaping_lab" / "ui" / "js" / "react" / "index_app.jsx"
INDEX_HTML = ROOT / "virtual_shaping_lab" / "ui" / "index.html"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_builder_route_has_explicit_resolve_plan_action():
    text = _read(INDEX_APP)
    assert "function BuilderRouteContainer" in text
    assert "Resolve Plan" in text
    assert "onResolvePlan" in text
    assert "resolvePlanFromBuilderContext" in text


def test_builder_route_renders_resolved_plan_hash_and_summary():
    text = _read(INDEX_APP)
    assert "Plan Status:" in text
    assert "Stable Hash:" in text
    assert "Unit Count:" in text
    assert "Total Trials:" in text
    assert "Flow:" in text
    assert "summarizeResolvedPlan" in text


def test_builder_context_resolve_uses_seeded_preset_handoff():
    text = _read(INDEX_APP)
    assert "builderDraftTranslator" in text
    assert "draft_to_payload" in text
    assert "apiClient.postJson(\"plan\", translatedPayload)" in text
    assert "Seed a preset first, then resolve plan." in text
    assert "stateApi.UI_EVENTS.PLAN_RESOLVE_REQUESTED" in text


def test_plan_resolve_summary_has_dedicated_styles():
    text = _read(INDEX_HTML)
    assert ".plan-resolve-summary" in text
    assert ".plan-resolve-summary code" in text

