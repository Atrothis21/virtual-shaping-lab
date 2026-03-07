from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INDEX_APP = ROOT / "virtual_shaping_lab" / "ui" / "js" / "react" / "index_app.jsx"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_report_route_uses_policy_driven_warning_and_blocking_for_mismatches():
    text = _read(INDEX_APP)
    assert "activeRoute === ROUTES.report.key && reportWarningMismatch" in text
    assert "activeRoute === ROUTES.report.key && reportBlockingMismatch" in text
    assert "Version mismatch detected" in text
    assert "Report detail rendering is blocked for" in text
    assert "Refresh Run Status" in text


def test_report_mismatch_detection_covers_template_and_schema():
    text = _read(INDEX_APP)
    assert "detectReportVersionMismatches" in text
    assert 'field: "record_schema_version"' in text
    assert 'field: "template_version_used"' in text
    assert 'severity: "blocking"' in text
    assert 'severity: "warning"' in text
