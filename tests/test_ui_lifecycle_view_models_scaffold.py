from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "virtual_shaping_lab" / "ui" / "js" / "react" / "lifecycle_view_models.js"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_lifecycle_view_model_module_exports_selector_api():
    text = _read(MODULE)
    assert "window.VSLReact.lifecycleViewModels" in text
    assert "selectRunLifecycleViewModel" in text
    assert "selectRunProvenanceViewModel" in text
    assert "selectReportLifecycleViewModel" in text
    assert "selectReportArtifactViewModel" in text
    assert "selectReportProvenanceViewModel" in text
    assert "detectRunVersionMismatches" in text
    assert "detectReportVersionMismatches" in text
    assert "buildLifecycleInstrumentView" in text


def test_lifecycle_view_model_module_normalizes_artifacts_and_tones():
    text = _read(MODULE)
    assert "normalizeArtifactHref" in text
    assert "inferFigureSemanticTone" in text
    assert "figureList" in text
    assert "tone: inferFigureSemanticTone(href)" in text
