from __future__ import annotations

from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
UI_PRESETS_DIR = ROOT / "virtual_shaping_lab" / "ui" / "presets"
JS_DIR = ROOT / "virtual_shaping_lab" / "ui" / "js" / "react"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _extract_js_object_keys(source: str, object_name: str) -> set[str]:
    m = re.search(rf"{re.escape(object_name)}\s*=\s*\{{(.*?)\}};", source, flags=re.S)
    assert m, f"Could not find object '{object_name}'."
    body = m.group(1)
    return set(re.findall(r"^\s*([a-z0-9_]+)\s*:", body, flags=re.M))


def _extract_js_array_values(source: str, array_name: str) -> list[str]:
    m = re.search(rf"{re.escape(array_name)}\s*=\s*\[(.*?)\];", source, flags=re.S)
    assert m, f"Could not find array '{array_name}'."
    return re.findall(r'"([a-z0-9_]+)"', m.group(1))


def test_all_preset_pages_include_teaching_scripts():
    html_files = sorted(UI_PRESETS_DIR.glob("*.html"))
    assert html_files, "No preset HTML files found."

    for html in html_files:
        text = _read(html)
        assert '/ui/js/react/teaching_panel.jsx' in text, f"Missing teaching_panel in {html.name}"
        assert '/ui/js/react/preset_focus_mode.jsx' in text, f"Missing preset_focus_mode in {html.name}"
        assert '/ui/js/react/preset_handoff.jsx' in text, f"Missing preset_handoff in {html.name}"


def test_teaching_order_and_focus_profiles_cover_same_presets():
    teaching_src = _read(JS_DIR / "teaching_panel.jsx")
    focus_src = _read(JS_DIR / "preset_focus_mode.jsx")

    order = set(_extract_js_array_values(teaching_src, "PRESET_ORDER"))
    focus_keys = _extract_js_object_keys(focus_src, "PRESET_FOCUS")

    assert order == focus_keys


def test_preset_catalog_includes_teaching_metadata_fields():
    catalog_src = _read(JS_DIR / "preset_catalog.jsx")

    assert "teaches:" in catalog_src
    assert "builderNext:" in catalog_src
    assert "nextPhenomenon:" in catalog_src
