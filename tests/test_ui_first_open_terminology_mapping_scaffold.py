from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LAUNCHER_ROUTE = ROOT / "virtual_shaping_lab" / "ui" / "js" / "react" / "routes" / "launcher_route.jsx"
PRESETS_ROUTE = ROOT / "virtual_shaping_lab" / "ui" / "js" / "react" / "routes" / "presets_route.jsx"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_entry_surfaces_use_experiment_type_wording():
    text = _read(LAUNCHER_ROUTE) + _read(PRESETS_ROUTE)
    assert "Experiment type:" in text
    assert "Sort<select" in text
    assert "Experiment type</option>" in text
    assert "Search preset, experiment type, signal..." in text


def test_preset_entry_actions_use_plain_language_verbs():
    text = _read(PRESETS_ROUTE)
    assert "Prepare preset" in text
    assert "Run preset" in text
    assert "Run preset + report" in text
    assert "Resolve Preset" not in text
    assert "Resolve + Run" not in text

