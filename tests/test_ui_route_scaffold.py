from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INDEX_APP = ROOT / "virtual_shaping_lab" / "ui" / "js" / "react" / "index_app.jsx"
INDEX_HTML = ROOT / "virtual_shaping_lab" / "ui" / "index.html"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_index_app_defines_first_pass_routes():
    text = _read(INDEX_APP)
    assert 'presets: { key: "presets"' in text
    assert 'builder: { key: "builder"' in text
    assert 'run: { key: "run"' in text
    assert 'report: { key: "report"' in text
    assert 'catalogHelp: { key: "catalogHelp"' in text
    assert '#/presets' in text
    assert '#/builder' in text
    assert '#/run' in text
    assert '#/report' in text
    assert '#/catalog-help' in text


def test_index_app_has_route_container_components():
    text = _read(INDEX_APP)
    assert "function PresetsRouteContainer()" in text
    assert "function BuilderRouteContainer()" in text
    assert "function RunRouteContainer()" in text
    assert "function ReportRouteContainer()" in text
    assert "function CatalogHelpRouteContainer()" in text
    assert "function renderActiveRoute()" in text


def test_index_app_initializes_from_hash_and_hashchange():
    text = _read(INDEX_APP)
    assert "parseRouteFromHash(window.location.hash)" in text
    assert 'window.addEventListener("hashchange", onHashChange)' in text
    assert "window.location.hash = route.hash" in text


def test_index_html_loads_react_shell_entrypoint():
    text = _read(INDEX_HTML)
    assert '<script type="text/babel" src="/ui/js/react/index_app.jsx"></script>' in text
    assert 'className="shell-layout"' not in text  # sanity: styles are in css, jsx is separate
