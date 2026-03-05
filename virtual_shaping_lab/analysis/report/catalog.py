"""Protocol-to-report-template mappings."""

from __future__ import annotations

import warnings

from analysis.domain.types import ReportTemplateSpec
from virtual_shaping_lab.domain.catalog_metadata import (
    UICatalogMetadata,
    make_default_ui_metadata,
    validate_ui_metadata_map,
)
from virtual_shaping_lab.domain.naming import normalize_protocol_key

DEFAULT_REPORT_BY_PROTOCOL: dict[str, str] = {
    "acquisition": "verification_report",
    "extinction": "verification_report",
    "rapid_reacquisition": "verification_report",
    "blocking": "verification_report",
    "overshadowing": "verification_report",
    "conditioned_inhibition": "verification_report",
    "aba_renewal": "verification_report",
    "abc_renewal": "verification_report",
    "aab_renewal": "verification_report",
    "operant_conditioning": "verification_report",
}

DEFAULT_TEMPLATE_BY_PROTOCOL: dict[str, ReportTemplateSpec] = {
    name: ReportTemplateSpec(
        report_name=report_name,
        metric_names=("mean_reward",),
        figure_names=("trial_curve", "tick_response_curve", "probe_bar"),
    )
    for name, report_name in DEFAULT_REPORT_BY_PROTOCOL.items()
}

FALLBACK_TEMPLATE = ReportTemplateSpec(
    report_name="verification_report",
    metric_names=("mean_reward",),
    figure_names=("trial_curve", "tick_response_curve", "probe_bar"),
)

REPORT_TEMPLATE_METADATA: dict[str, UICatalogMetadata] = {
    key: make_default_ui_metadata(key, description_prefix="Default report template")
    for key in DEFAULT_TEMPLATE_BY_PROTOCOL.keys()
}
validate_ui_metadata_map(
    keys=set(DEFAULT_TEMPLATE_BY_PROTOCOL.keys()),
    metadata_map=REPORT_TEMPLATE_METADATA,
    namespace="analysis.report.catalog",
)


def get_default_report_for_protocol(protocol_name: str) -> str:
    normalized = normalize_protocol_key(protocol_name)
    return DEFAULT_REPORT_BY_PROTOCOL.get(normalized, "verification_report")


def get_report_template_metadata(protocol_name: str) -> UICatalogMetadata:
    normalized = normalize_protocol_key(protocol_name)
    if normalized in REPORT_TEMPLATE_METADATA:
        return REPORT_TEMPLATE_METADATA[normalized]
    return make_default_ui_metadata("verification_report", description_prefix="Fallback report template")


def get_default_template_for_protocol(protocol_name: str) -> ReportTemplateSpec:
    normalized = normalize_protocol_key(protocol_name)
    if normalized not in DEFAULT_TEMPLATE_BY_PROTOCOL:
        available = ", ".join(sorted(DEFAULT_TEMPLATE_BY_PROTOCOL.keys()))
        warnings.warn(
            f"No default report template mapping for protocol '{protocol_name}' "
            f"(normalized='{normalized}'). Using fallback verification template. "
            f"Available mappings: {available}",
            UserWarning,
            stacklevel=2,
        )
        return FALLBACK_TEMPLATE
    return DEFAULT_TEMPLATE_BY_PROTOCOL[normalized]
