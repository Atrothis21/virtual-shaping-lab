"""Protocol-to-report-template mappings."""

from __future__ import annotations

from analysis.domain.types import ReportTemplateSpec

DEFAULT_REPORT_BY_PROTOCOL: dict[str, str] = {
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


def get_default_report_for_protocol(protocol_name: str) -> str:
    return DEFAULT_REPORT_BY_PROTOCOL.get(protocol_name, "verification_report")


def get_default_template_for_protocol(protocol_name: str) -> ReportTemplateSpec:
    return DEFAULT_TEMPLATE_BY_PROTOCOL.get(protocol_name, FALLBACK_TEMPLATE)
