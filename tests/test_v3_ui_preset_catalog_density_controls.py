from __future__ import annotations

from pathlib import Path

from api import run as api_run


ROOT = Path(__file__).resolve().parents[1]
JS_DIR = ROOT / "virtual_shaping_lab" / "ui" / "js" / "react"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_preset_ux_catalog_declares_density_controls_contract_values():
    body = api_run.preset_ux_catalog_api()
    controls = body.get("ui_density_controls", {})
    assert isinstance(controls.get("collapse_sections_when_card_count_gt"), int)
    assert isinstance(controls.get("top_recommended_limit"), int)
    assert controls.get("show_more_enabled") is True


def test_presets_app_applies_density_controls_and_show_more_toggle_behavior():
    src = _read(JS_DIR / "app.jsx")
    assert "collapse_sections_when_card_count_gt" in src
    assert "top_recommended_limit" in src
    assert "Show More" in src
    assert "Show Less" in src
    assert "recommendedTop" in src
