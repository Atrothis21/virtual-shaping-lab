# api/run.py

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path
import traceback
import copy

from ui.validate_payload import validate_payload
from experiment.config import ExperimentConfig
from experiment.assemble import assemble_experiment
from experiment.runner import Runner
from analysis.report.report import run_report


app = FastAPI(title="Virtual Shaping Lab API")

PACKAGE_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = PACKAGE_ROOT.parent
UI_DIR = PACKAGE_ROOT / "ui"

app.mount("/ui", StaticFiles(directory=str(UI_DIR)), name="ui")

reports_dir = REPO_ROOT / "reports"
reports_dir.mkdir(parents=True, exist_ok=True)
app.mount("/reports", StaticFiles(directory=str(reports_dir)), name="reports")


@app.get("/")
def root():
    return FileResponse(str(UI_DIR / "index.html"))

# Orchestration helper: keeps API thin.
# Responsibility: run config → assemble objects → run protocols → generate report.
# Returns only data needed by the HTTP response layer.
def _run_experiment(raw_payload: dict):
    config = ExperimentConfig.from_payload(raw_payload)
    protocols, agent, representation = assemble_experiment(config)

    records = []
    for phase_index, protocol in enumerate(protocols):
        runner = Runner(protocol)
        phase_records = runner.run()

        for r in phase_records:
            r["phase"] = phase_index
            from experiment.runtime_records import finalize_record
            finalize_record(
                r,
                phase_name=config.phases[phase_index].name,
            )

        records.extend(phase_records)

    report_dir = run_report(
        records=records,
        preset=config.report_preset,
        payload=raw_payload,
        output_dir=str(reports_dir),
    )

    report_dir = Path(report_dir)

    artifacts = {
        "pdf": str(report_dir / "report.pdf"),
        "figures": [str(p) for p in report_dir.glob("*.png")]
    }

    return records, report_dir, artifacts

# HTTP handler: validation + error translation only.
# Any experiment logic belongs in _run_experiment().
@app.post("/run")
def run_api(payload: dict):
    print("=== /run called ===", flush=True)

    try:
        raw_payload = copy.deepcopy(payload)
        validate_payload(raw_payload)
        print("Payload validated", flush=True)
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Payload validation failed: {str(e)}"
        )

    try:
        print("Parsing ExperimentConfig", flush=True)
        records, report_dir, artifacts = _run_experiment(raw_payload)

        print(f"Run complete ({len(records)} records)", flush=True)
        print("=== /run completed successfully ===", flush=True)

        return {
            "status": "success",
            "run_id": report_dir.name,
            "artifacts": artifacts
        }

    except Exception as e:
        print("=== /run ERROR ===", flush=True)
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
