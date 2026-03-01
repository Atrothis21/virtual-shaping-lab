"""Protocol-to-report-template mappings."""

from __future__ import annotations


DEFAULT_REPORT_BY_PROTOCOL: dict[str, str] = {
    "extinction": "verification_report",
    "rapid_reacquisition": "verification_report",
    "blocking": "verification_report",
}


def get_default_report_for_protocol(protocol_name: str) -> str:
    return DEFAULT_REPORT_BY_PROTOCOL.get(protocol_name, "verification_report")
