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
    assert "function PresetsRouteContainer(" in text
    assert "function BuilderRouteContainer(" in text
    assert "function RunRouteContainer(" in text
    assert "function ReportRouteContainer(" in text
    assert "function CatalogHelpRouteContainer()" in text
    assert "function renderActiveRoute()" in text


def test_index_app_initializes_from_hash_and_hashchange():
    text = _read(INDEX_APP)
    assert "parseRouteFromHash(window.location.hash)" in text
    assert 'window.addEventListener("hashchange", onHashChange)' in text
    assert "window.location.hash = route.hash" in text


def test_index_html_loads_react_shell_entrypoint():
    text = _read(INDEX_HTML)
    theme_idx = text.find('/ui/js/react/ui_theme_tokens.js')
    api_idx = text.find('/ui/js/react/api_client.js')
    state_idx = text.find('/ui/js/react/state_domains.js')
    read_models_idx = text.find('/ui/js/react/preset_read_models.js')
    action_service_idx = text.find('/ui/js/react/preset_action_service.js')
    contracts_idx = text.find('/ui/js/react/ui_architecture_contracts.js')
    foundation_idx = text.find('/ui/js/react/ui_foundation_primitives.jsx')
    primitives_idx = text.find('/ui/js/react/ui_primitives.jsx')
    app_idx = text.find('/ui/js/react/index_app.jsx')
    assert theme_idx != -1
    assert api_idx != -1
    assert state_idx != -1
    assert read_models_idx != -1
    assert action_service_idx != -1
    assert contracts_idx != -1
    assert foundation_idx != -1
    assert primitives_idx != -1
    assert app_idx != -1
    assert theme_idx < app_idx
    assert api_idx < app_idx
    assert state_idx < app_idx
    assert read_models_idx < app_idx
    assert action_service_idx < app_idx
    assert contracts_idx < app_idx
    assert foundation_idx < app_idx
    assert primitives_idx < app_idx
    assert '<script type="text/babel" src="/ui/js/react/index_app.jsx"></script>' in text
    assert 'className="shell-layout"' not in text  # sanity: styles are in css, jsx is separate


def test_index_app_bootstraps_catalog_and_surfaces_versions():
    text = _read(INDEX_APP)
    assert "window.VSLApi.createApiClient" in text
    assert "apiClient.getJson(\"catalog/extensions\")" in text
    assert "stateApi.UI_EVENTS.CATALOG_REFRESH_REQUESTED" in text
    assert "stateApi.UI_EVENTS.CATALOG_REFRESH_SUCCEEDED" in text
    assert "stateApi.UI_EVENTS.CATALOG_REFRESH_FAILED" in text
    assert "Catalog bootstrap status:" in text
    assert "catalog_version" in text
    assert "record_schema_version" in text
    assert "template_version_used" in text
    assert "GlobalBanner" in text
    assert "BlockingPanel" in text
    assert "NotificationStack" in text
    assert "buildCatalogMismatchBanner" in text
    assert "Catalog unavailable" in text
    assert "window.VSLReact.foundationPrimitives" in text
    assert "window.VSLReact.architectureContracts" in text
    assert "createDefaultContractRegistry()" in text
    assert "SurfacePanel" in text
    assert "StatusBadge" in text
