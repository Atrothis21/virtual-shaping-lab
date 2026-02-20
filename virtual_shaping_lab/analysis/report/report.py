import json
from pathlib import Path
from datetime import datetime

from analysis.report.presets import get_report_preset
from analysis.metrics.registry import METRIC_REGISTRY
from analysis.visualizations.registry import VISUALIZATION_REGISTRY


def run_report(
    records,
    preset: str,
    payload=None,
    output_dir: str = "reports",
):
    """
    Generate analysis outputs and figures from experiment records
    using a named report preset.
    """
    # -------------------------------------------------
    # Resolve preset
    # -------------------------------------------------
    report_config = get_report_preset(preset)

    # -------------------------------------------------
    # Create report directory
    # -------------------------------------------------
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    report_dir = Path(output_dir) / timestamp
    report_dir.mkdir(parents=True, exist_ok=False)

    # -------------------------------------------------
    # Save provenance + trial records
    # -------------------------------------------------
    if payload is not None:
        with open(report_dir / "payload.json", "w") as f:
            json.dump(payload, f, indent=2)
        attention = payload.get("experiment", {}).get("attention")
        if isinstance(attention, dict):
            with open(report_dir / "attention_summary.json", "w") as f:
                json.dump(attention, f, indent=2)

    with open(report_dir / "records.json", "w") as f:
        json.dump(records, f, indent=2)

    # -------------------------------------------------
    # Compute metrics (optional, for reuse or advanced plots)
    # -------------------------------------------------
    metrics = {}

    for metric_name in report_config.metrics:
        if metric_name not in METRIC_REGISTRY:
            raise KeyError(f"Unknown metric '{metric_name}'")

        metric_cls = METRIC_REGISTRY[metric_name]
        metric_kwargs = report_config.params.get(metric_name, {})

        metric = metric_cls(**metric_kwargs)
        metrics[metric_name] = metric.compute(records)

    # -------------------------------------------------
    # Render visualizations
    # -------------------------------------------------
    figures = []

    for viz_name in report_config.visualizations:
        if viz_name not in VISUALIZATION_REGISTRY:
            raise KeyError(f"Unknown visualization '{viz_name}'")

        viz_cls = VISUALIZATION_REGISTRY[viz_name]
        viz = viz_cls()

        viz_params = report_config.params.get(viz_name, {})
        phase_names = viz_params.get("phase_names")

        filtered_records = records
        if phase_names:
            filtered_records = [
                r for r in records
                if r.get("phase") in phase_names
                or r.get("phase_name") in phase_names
                or r.get("subphase_name") in phase_names
            ]

        viz.render(
            records=filtered_records,
            metrics=metrics,
        )

        fig_path = report_dir / f"{viz_name}.png"
        viz.save(fig_path)

        figures.append(str(fig_path))

    return report_dir
