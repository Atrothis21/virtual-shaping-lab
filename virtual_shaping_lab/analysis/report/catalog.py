"""Protocol-to-report-template mappings."""

from __future__ import annotations

import warnings

from analysis.domain.types import ReportTemplateSpec
from virtual_shaping_lab.domain.catalog_metadata import (
    CONSTRAINT_ACQUISITION_COMPATIBLE,
    CONSTRAINT_ANALYSIS_DEFAULT_TEMPLATE,
    CONSTRAINT_CUE_COMPETITION_COMPATIBLE,
    CONSTRAINT_EXTINCTION_COMPATIBLE,
    CONSTRAINT_FALLBACK_TEMPLATE,
    CONSTRAINT_INHIBITION_COMPATIBLE,
    CONSTRAINT_OPERANT_COMPATIBLE,
    CONSTRAINT_RENEWAL_COMPATIBLE,
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

_DEFAULT_TEMPLATE_METADATA = UICatalogMetadata(
    label="Verification Report Template",
    description="Default verification report bundle for protocol-level analysis.",
    params_schema={
        "report_name": {"type": "str"},
        "metric_names": {"type": "list[str]"},
        "figure_names": {"type": "list[str]"},
    },
    defaults={
        "report_name": "verification_report",
        "metric_names": ["mean_reward"],
        "figure_names": ["trial_curve", "tick_response_curve", "probe_bar"],
    },
    constraints=(CONSTRAINT_ANALYSIS_DEFAULT_TEMPLATE,),
    examples=(
        {
            "report_name": "verification_report",
            "metric_names": ["mean_reward"],
            "figure_names": ["trial_curve", "tick_response_curve", "probe_bar"],
        },
    ),
)

REPORT_TEMPLATE_METADATA: dict[str, UICatalogMetadata] = {
    "acquisition": UICatalogMetadata(
        label="Acquisition Report Template",
        description="Default analysis template for acquisition-style protocols.",
        params_schema=dict(_DEFAULT_TEMPLATE_METADATA.params_schema),
        defaults=dict(_DEFAULT_TEMPLATE_METADATA.defaults),
        constraints=_DEFAULT_TEMPLATE_METADATA.constraints + (CONSTRAINT_ACQUISITION_COMPATIBLE,),
        examples=_DEFAULT_TEMPLATE_METADATA.examples,
    ),
    "extinction": UICatalogMetadata(
        label="Extinction Report Template",
        description="Default analysis template for extinction and reacquisition protocols.",
        params_schema=dict(_DEFAULT_TEMPLATE_METADATA.params_schema),
        defaults=dict(_DEFAULT_TEMPLATE_METADATA.defaults),
        constraints=_DEFAULT_TEMPLATE_METADATA.constraints + (CONSTRAINT_EXTINCTION_COMPATIBLE,),
        examples=_DEFAULT_TEMPLATE_METADATA.examples,
    ),
    "rapid_reacquisition": UICatalogMetadata(
        label="Rapid Reacquisition Report Template",
        description="Default template for rapid-reacquisition outcome verification.",
        params_schema=dict(_DEFAULT_TEMPLATE_METADATA.params_schema),
        defaults=dict(_DEFAULT_TEMPLATE_METADATA.defaults),
        constraints=_DEFAULT_TEMPLATE_METADATA.constraints + (CONSTRAINT_EXTINCTION_COMPATIBLE,),
        examples=_DEFAULT_TEMPLATE_METADATA.examples,
    ),
    "blocking": UICatalogMetadata(
        label="Blocking Report Template",
        description="Default template for cue-competition phenomena such as blocking.",
        params_schema=dict(_DEFAULT_TEMPLATE_METADATA.params_schema),
        defaults=dict(_DEFAULT_TEMPLATE_METADATA.defaults),
        constraints=_DEFAULT_TEMPLATE_METADATA.constraints + (CONSTRAINT_CUE_COMPETITION_COMPATIBLE,),
        examples=_DEFAULT_TEMPLATE_METADATA.examples,
    ),
    "overshadowing": UICatalogMetadata(
        label="Overshadowing Report Template",
        description="Default template for cue-competition phenomena such as overshadowing.",
        params_schema=dict(_DEFAULT_TEMPLATE_METADATA.params_schema),
        defaults=dict(_DEFAULT_TEMPLATE_METADATA.defaults),
        constraints=_DEFAULT_TEMPLATE_METADATA.constraints + (CONSTRAINT_CUE_COMPETITION_COMPATIBLE,),
        examples=_DEFAULT_TEMPLATE_METADATA.examples,
    ),
    "conditioned_inhibition": UICatalogMetadata(
        label="Conditioned Inhibition Report Template",
        description="Default template for conditioned inhibition protocols.",
        params_schema=dict(_DEFAULT_TEMPLATE_METADATA.params_schema),
        defaults=dict(_DEFAULT_TEMPLATE_METADATA.defaults),
        constraints=_DEFAULT_TEMPLATE_METADATA.constraints + (CONSTRAINT_INHIBITION_COMPATIBLE,),
        examples=_DEFAULT_TEMPLATE_METADATA.examples,
    ),
    "aba_renewal": UICatalogMetadata(
        label="ABA Renewal Report Template",
        description="Default template for ABA renewal context-shift protocols.",
        params_schema=dict(_DEFAULT_TEMPLATE_METADATA.params_schema),
        defaults=dict(_DEFAULT_TEMPLATE_METADATA.defaults),
        constraints=_DEFAULT_TEMPLATE_METADATA.constraints + (CONSTRAINT_RENEWAL_COMPATIBLE,),
        examples=_DEFAULT_TEMPLATE_METADATA.examples,
    ),
    "abc_renewal": UICatalogMetadata(
        label="ABC Renewal Report Template",
        description="Default template for ABC renewal context-shift protocols.",
        params_schema=dict(_DEFAULT_TEMPLATE_METADATA.params_schema),
        defaults=dict(_DEFAULT_TEMPLATE_METADATA.defaults),
        constraints=_DEFAULT_TEMPLATE_METADATA.constraints + (CONSTRAINT_RENEWAL_COMPATIBLE,),
        examples=_DEFAULT_TEMPLATE_METADATA.examples,
    ),
    "aab_renewal": UICatalogMetadata(
        label="AAB Renewal Report Template",
        description="Default template for AAB renewal context-shift protocols.",
        params_schema=dict(_DEFAULT_TEMPLATE_METADATA.params_schema),
        defaults=dict(_DEFAULT_TEMPLATE_METADATA.defaults),
        constraints=_DEFAULT_TEMPLATE_METADATA.constraints + (CONSTRAINT_RENEWAL_COMPATIBLE,),
        examples=_DEFAULT_TEMPLATE_METADATA.examples,
    ),
    "operant_conditioning": UICatalogMetadata(
        label="Operant Conditioning Report Template",
        description="Default template for operant schedule protocols.",
        params_schema=dict(_DEFAULT_TEMPLATE_METADATA.params_schema),
        defaults=dict(_DEFAULT_TEMPLATE_METADATA.defaults),
        constraints=_DEFAULT_TEMPLATE_METADATA.constraints + (CONSTRAINT_OPERANT_COMPATIBLE,),
        examples=_DEFAULT_TEMPLATE_METADATA.examples,
    ),
}

for key in DEFAULT_TEMPLATE_BY_PROTOCOL.keys():
    if key not in REPORT_TEMPLATE_METADATA:
        REPORT_TEMPLATE_METADATA[key] = make_default_ui_metadata(
            key,
            description_prefix="Default report template",
        )

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
    return UICatalogMetadata(
        label="Fallback Verification Report Template",
        description="Fallback template used when no protocol-specific template metadata mapping exists.",
        params_schema=dict(_DEFAULT_TEMPLATE_METADATA.params_schema),
        defaults=dict(_DEFAULT_TEMPLATE_METADATA.defaults),
        constraints=_DEFAULT_TEMPLATE_METADATA.constraints + (CONSTRAINT_FALLBACK_TEMPLATE,),
        examples=_DEFAULT_TEMPLATE_METADATA.examples,
    )


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
