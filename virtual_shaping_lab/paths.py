from pathlib import Path


PACKAGE_ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = PACKAGE_ROOT.parent
UI_DIR = PACKAGE_ROOT / "ui"
REPORTS_DIR = PROJECT_ROOT / "reports"

