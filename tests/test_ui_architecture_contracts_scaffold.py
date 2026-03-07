from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTRACTS_JS = ROOT / "virtual_shaping_lab" / "ui" / "js" / "react" / "ui_architecture_contracts.js"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_architecture_contracts_exports_contract_builders():
    text = _read(CONTRACTS_JS)
    assert "createRouteContainerContract" in text
    assert "createDomainHookContract" in text
    assert "createApiServiceContract" in text
    assert "createDefaultContractRegistry" in text
    assert "window.VSLReact.architectureContracts" in text


def test_architecture_contracts_include_standard_patterns():
    text = _read(CONTRACTS_JS)
    assert "STANDARD_PATTERNS" in text
    assert "route_container" in text
    assert "domain_hook" in text
    assert "api_service" in text
    assert "forbidden" in text


def test_architecture_contracts_default_registry_has_first_pass_contracts():
    text = _read(CONTRACTS_JS)
    assert "AppShellRouteContainer" in text
    assert "CatalogBootstrapService" in text
    assert "useCatalogBootstrapState" in text
