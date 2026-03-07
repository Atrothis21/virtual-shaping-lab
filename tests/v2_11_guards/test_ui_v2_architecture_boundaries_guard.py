from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] / "virtual_shaping_lab" / "ui" / "js" / "react"
BOUNDARY_CONFIG = ROOT / "architecture_boundaries.json"


IMPORT_RE = re.compile(
    r'^\s*import\s+(?:.+?\s+from\s+)?["\'](?P<spec>[^"\']+)["\']',
    re.MULTILINE,
)


def _load_config() -> dict:
    return json.loads(BOUNDARY_CONFIG.read_text(encoding="utf-8"))


def _iter_import_specs(source: str) -> list[str]:
    return [m.group("spec") for m in IMPORT_RE.finditer(source)]


def _resolve_local_import_target(src_file: Path, import_spec: str) -> Path | None:
    if not import_spec.startswith("."):
        return None
    base = (src_file.parent / import_spec).resolve()
    candidates = [
        base,
        base.with_suffix(".js"),
        base.with_suffix(".jsx"),
        base / "index.js",
        base / "index.jsx",
    ]
    for cand in candidates:
        if cand.exists():
            return cand
    return None


def test_ui_boundary_config_is_present_and_valid():
    cfg = _load_config()
    assert "layers" in cfg and isinstance(cfg["layers"], list) and cfg["layers"]
    assert "allowed_dependencies" in cfg and isinstance(cfg["allowed_dependencies"], dict)
    assert "file_layers" in cfg and isinstance(cfg["file_layers"], dict) and cfg["file_layers"]
    assert "forbidden_direct_fetch_outside" in cfg and isinstance(cfg["forbidden_direct_fetch_outside"], list)


def test_ui_file_layer_mappings_reference_existing_files():
    cfg = _load_config()
    missing = []
    invalid_layers = []
    valid_layers = set(cfg["layers"])
    for rel_name, layer in cfg["file_layers"].items():
        if layer not in valid_layers:
            invalid_layers.append((rel_name, layer))
        if not (ROOT / rel_name).exists():
            missing.append(rel_name)
    assert not invalid_layers, f"Invalid file->layer mappings: {invalid_layers}"
    assert not missing, f"Mapped UI files do not exist: {missing}"


def test_ui_layer_dependency_direction_guard():
    cfg = _load_config()
    file_layers: dict[str, str] = cfg["file_layers"]
    allowed_dependencies: dict[str, list[str]] = cfg["allowed_dependencies"]

    file_for_path = {(ROOT / rel).resolve(): rel for rel in file_layers}
    violations: list[tuple[str, str, str, str]] = []

    for rel_src, src_layer in file_layers.items():
        src_path = (ROOT / rel_src).resolve()
        source = src_path.read_text(encoding="utf-8")
        for spec in _iter_import_specs(source):
            target_path = _resolve_local_import_target(src_path, spec)
            if target_path is None:
                continue
            rel_target = file_for_path.get(target_path.resolve())
            if rel_target is None:
                # Import target is outside guarded mapping; ignore for now.
                continue
            target_layer = file_layers[rel_target]
            if target_layer not in allowed_dependencies.get(src_layer, []):
                violations.append((rel_src, src_layer, rel_target, target_layer))

    assert not violations, (
        "UI layer dependency violations (source_file, source_layer, target_file, target_layer): "
        f"{violations}"
    )


def test_ui_direct_fetch_is_restricted_to_shared_api_client():
    cfg = _load_config()
    allow_fetch = set(cfg["forbidden_direct_fetch_outside"])

    violations: list[str] = []
    for rel_name in cfg["file_layers"].keys():
        src = ROOT / rel_name
        source = src.read_text(encoding="utf-8")
        if "fetch(" in source and rel_name not in allow_fetch:
            violations.append(rel_name)

    assert not violations, (
        "Direct fetch(...) usage is forbidden outside shared API client. Violations: "
        f"{violations}"
    )
