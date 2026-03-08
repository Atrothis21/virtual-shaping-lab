from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] / "virtual_shaping_lab" / "ui" / "js" / "react"
ROUTES_DIR = ROOT / "routes"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_routes_do_not_call_api_client_directly():
    violations: list[tuple[str, str]] = []
    forbidden_markers = ('apiClient.postJson(', 'apiClient.getJson(', 'fetch(')
    for path in sorted(ROUTES_DIR.glob("*.jsx")):
        text = _read(path)
        for marker in forbidden_markers:
            if marker in text:
                violations.append((path.name, marker))

    assert not violations, (
        "Route files must not perform direct API calls; use route handlers/services instead. "
        f"Violations: {violations}"
    )


def test_builder_translation_call_is_limited_to_plan_workflow_boundary():
    allowed_call_sites = {
        "builder_draft_translator.js",
        "plan_workflow_service.js",
    }
    violations: list[str] = []
    for path in sorted(ROOT.rglob("*")):
        if path.suffix not in {".js", ".jsx"}:
            continue
        text = _read(path)
        if "draft_to_payload(" not in text:
            continue
        if path.name not in allowed_call_sites:
            violations.append(str(path.relative_to(ROOT)))

    assert not violations, (
        "draft_to_payload(...) calls are restricted to translator and plan workflow boundary. "
        f"Violations: {violations}"
    )


def test_builder_plan_post_uses_translated_payload_not_draft_seed():
    workflow = _read(ROOT / "plan_workflow_service.js")
    assert 'apiClient.postJson("plan", translatedPayload)' in workflow
    assert 'apiClient.postJson("plan", draftSeed)' not in workflow

