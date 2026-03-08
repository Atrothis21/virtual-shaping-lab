from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
THEME_TOKENS_JS = ROOT / "virtual_shaping_lab" / "ui" / "js" / "react" / "ui_theme_tokens.js"
INDEX_HTML = ROOT / "virtual_shaping_lab" / "ui" / "index.html"
INDEX_CSS = ROOT / "virtual_shaping_lab" / "ui" / "css" / "index.css"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_theme_token_module_exposes_required_token_groups():
    text = _read(THEME_TOKENS_JS)
    assert "VSL_THEME_TOKENS" in text
    assert "color:" in text
    assert "semantic:" in text
    assert "typography:" in text
    assert "spacing:" in text
    assert "radius:" in text
    assert "elevation:" in text
    assert "window.VSLReact.themeTokens" in text


def test_theme_tokens_include_behavioral_semantic_colors():
    text = _read(THEME_TOKENS_JS)
    assert "csPlus" in text
    assert "csMinus" in text
    assert "probe" in text
    assert "compound" in text
    assert "learning" in text


def test_index_css_uses_theme_css_variables():
    text = _read(INDEX_CSS)
    assert "--vsl-color-bg" in text
    assert "--vsl-color-panel" in text
    assert "--vsl-color-cs-plus" in text
    assert "--vsl-font-sans" in text
    assert "var(--vsl-color-bg)" in text
    assert "var(--vsl-color-panel)" in text
