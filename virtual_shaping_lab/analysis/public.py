"""Public analysis facade.

Stable high-level entrypoints for report execution and default-template lookup.
"""

from __future__ import annotations

from typing import Any

from analysis.registry import run_protocol_default_report
from analysis.report.catalog import DEFAULT_TEMPLATE_BY_PROTOCOL, get_default_template_for_protocol
from analysis.report.report import run_report
from virtual_shaping_lab.domain.naming import normalize_protocol_key


def run_preset_report(
    *,
    records: list[dict[str, Any]],
    preset: str,
    payload: dict[str, Any] | None = None,
    output_dir: str | None = None,
):
    """Run report generation using a named preset."""
    return run_report(records=records, preset=preset, payload=payload, output_dir=output_dir)


def run_default_protocol_report(
    *,
    protocol_name: str,
    records: list[dict[str, Any]],
    out_dir: str,
    ctx=None,
):
    """Run the default report template mapped to a protocol key."""
    return run_protocol_default_report(protocol_name=protocol_name, records=records, out_dir=out_dir, ctx=ctx)


def get_protocol_default_template(protocol_name: str):
    """Resolve protocol -> default report template specification."""
    return get_default_template_for_protocol(protocol_name)


def list_protocol_default_templates() -> dict[str, dict[str, Any]]:
    """Return protocol -> default template metadata mapping."""
    templates: dict[str, dict[str, Any]] = {}
    for protocol_name, spec in DEFAULT_TEMPLATE_BY_PROTOCOL.items():
        normalized = normalize_protocol_key(protocol_name)
        templates[normalized] = {
            "report_name": spec.report_name,
            "template_version": spec.template_version,
            "metric_names": list(spec.metric_names),
            "figure_names": list(spec.figure_names),
        }
    return {k: templates[k] for k in sorted(templates.keys())}
