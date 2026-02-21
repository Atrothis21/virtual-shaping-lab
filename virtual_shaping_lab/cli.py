# cli.py

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def _ensure_repo_paths() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))
    vsl_root = repo_root / "virtual_shaping_lab"
    if str(vsl_root) not in sys.path:
        sys.path.insert(0, str(vsl_root))


def _load_payload(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(f"Payload file not found: {path}")
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _cmd_run(args: argparse.Namespace) -> int:
    _ensure_repo_paths()
    from ui.validate_payload import validate_payload
    from api.run import _run_experiment

    payload = _load_payload(Path(args.payload))
    validate_payload(payload)

    _, report_dir, artifacts = _run_experiment(payload)

    print(f"Run complete: {report_dir}")
    print(json.dumps({"artifacts": artifacts}, indent=2))
    return 0


def _cmd_validate(args: argparse.Namespace) -> int:
    _ensure_repo_paths()
    from ui.validate_payload import validate_payload

    payload = _load_payload(Path(args.payload))
    validate_payload(payload)
    print("Payload validated.")
    return 0


def _cmd_serve(args: argparse.Namespace) -> int:
    _ensure_repo_paths()
    try:
        import uvicorn
    except ImportError as exc:
        raise SystemExit(
            "uvicorn is required for 'vsl serve'. "
            "Install it with: pip install uvicorn"
        ) from exc

    uvicorn.run(
        "api.run:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
    )
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="vsl",
        description="Virtual Shaping Lab CLI",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    run = sub.add_parser("run", help="Run a payload JSON file.")
    run.add_argument("payload", help="Path to payload JSON.")
    run.set_defaults(func=_cmd_run)

    validate = sub.add_parser("validate", help="Validate a payload JSON file.")
    validate.add_argument("payload", help="Path to payload JSON.")
    validate.set_defaults(func=_cmd_validate)

    serve = sub.add_parser("serve", help="Start the local API server.")
    serve.add_argument("--host", default="127.0.0.1")
    serve.add_argument("--port", type=int, default=8000)
    serve.add_argument("--reload", action="store_true")
    serve.set_defaults(func=_cmd_serve)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
