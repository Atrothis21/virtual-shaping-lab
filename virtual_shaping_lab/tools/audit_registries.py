import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from experiment.factories.protocol_factory import PROTOCOL_REGISTRY
from analysis.report.presets import get_report_preset
from experiment.phases.catalog import PHASE_CATALOG


SCHEMA_DIR = Path(__file__).resolve().parents[1] / "ui" / "schema"
PHASE_SCHEMA_DIR = SCHEMA_DIR / "phases"
PROTOCOL_SCHEMA_DIR = SCHEMA_DIR / "protocols"


def _schema_keys(schema_dir: Path) -> set[str]:
    if not schema_dir.exists():
        return set()
    return {
        p.name.replace(".schema.json", "")
        for p in schema_dir.glob("*.schema.json")
    }


def audit():
    protocol_keys = set(PROTOCOL_REGISTRY.keys())
    phase_keys = set(PHASE_CATALOG.keys())

    protocol_schema_keys = _schema_keys(PROTOCOL_SCHEMA_DIR)
    phase_schema_keys = _schema_keys(PHASE_SCHEMA_DIR)

    missing_protocol_schemas = sorted(protocol_keys - protocol_schema_keys)
    missing_phase_schemas = sorted(phase_keys - phase_schema_keys)

    missing_report_presets = []
    for name in sorted(protocol_keys):
        try:
            _ = get_report_preset(name)
        except Exception:
            missing_report_presets.append(name)

    print("Missing protocol schemas:", missing_protocol_schemas)
    print("Missing phase schemas:", missing_phase_schemas)
    print("Missing report presets:", missing_report_presets)


if __name__ == "__main__":
    audit()
