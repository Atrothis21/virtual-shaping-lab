# analysis/report/io.py

from pathlib import Path
from datetime import datetime
import json

def create_report_dir(base_dir: str = "reports") -> Path:
    """
    Create a timestamped report directory.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    root = Path(base_dir) / timestamp

    (root / "metrics").mkdir(parents=True, exist_ok=True)
    (root / "figures").mkdir(parents=True, exist_ok=True)

    return root

def save_metric_output(
    metric_name: str,
    result,
    metrics_dir,
):
    path = metrics_dir / f"{metric_name}.json"

    with open(path, "w") as f:
        json.dump(result, f, indent=2)

