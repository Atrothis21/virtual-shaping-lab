import json
from pathlib import Path
from datetime import datetime

from analysis.report.presets import get_report_preset
from analysis.metrics.registry import METRIC_REGISTRY
from analysis.visualizations.registry import VISUALIZATION_REGISTRY
from analysis.report.pdf import ReportPDF

PACKAGE_ROOT = Path(__file__).resolve().parents[2]
REPO_ROOT = PACKAGE_ROOT.parent
DEFAULT_REPORTS_DIR = REPO_ROOT / "reports"


def _to_jsonable(value):
    if isinstance(value, dict):
        return {str(k): _to_jsonable(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_to_jsonable(v) for v in value]
    if isinstance(value, tuple):
        return [_to_jsonable(v) for v in value]
    return value


def run_report(
    records,
    preset: str,
    payload=None,
    output_dir: str | None = None,
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
    base_dir = Path(output_dir) if output_dir is not None else DEFAULT_REPORTS_DIR
    report_dir = base_dir / timestamp
    report_dir.mkdir(parents=True, exist_ok=False)
    metrics_dir = report_dir / "metrics"
    metrics_dir.mkdir(parents=True, exist_ok=True)

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
        with open(metrics_dir / f"{metric_name}.json", "w") as f:
            json.dump(_to_jsonable(metrics[metric_name]), f, indent=2)

    # -------------------------------------------------
    # Render visualizations
    # -------------------------------------------------
    figures = []

    pdf = ReportPDF(report_dir / "report.pdf")
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
        if getattr(viz, "fig", None) is not None:
            pdf.add_figure(viz.fig, viz_name)
        viz.save(fig_path)

        figures.append(str(fig_path))

    for metric_name, metric_result in metrics.items():
        pdf.add_metric_text(metric_name, _to_jsonable(metric_result))
    pdf.close()

    return report_dir
