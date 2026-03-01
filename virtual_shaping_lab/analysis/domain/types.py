"""Analysis-layer boundary types."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass(frozen=True)
class MetricResult:
    name: str
    value: Any
    series: Optional[list[Any]] = None
    meta: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class FigureResult:
    name: str
    path: str
    meta: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ReportResult:
    name: str
    output_dir: str
    artifacts: dict[str, Any] = field(default_factory=dict)
    meta: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ReportTemplateSpec:
    """Default compositional report bundle for a protocol."""

    report_name: str
    template_version: int = 1
    metric_names: tuple[str, ...] = ()
    figure_names: tuple[str, ...] = ()
    meta: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class AnalysisContext:
    plan_hash: Optional[str] = None
    protocol_path: Optional[str] = None
    update_mode: Optional[str] = None
    record_mode: Optional[str] = None
    dt_s: Optional[float] = None
    extra: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_records(cls, records: list[dict[str, Any]]) -> "AnalysisContext":
        if not records:
            return cls()

        first = records[0]
        meta = first.get("metadata", {}) if isinstance(first.get("metadata"), dict) else {}
        extra = {}
        if isinstance(meta, dict):
            extra = {k: v for k, v in meta.items() if k not in {"plan_hash", "protocol_path", "update_mode", "record_mode"}}
        return cls(
            plan_hash=meta.get("plan_hash"),
            protocol_path=first.get("unit_path") or meta.get("protocol_path"),
            update_mode=meta.get("update_mode"),
            record_mode=("tick" if first.get("tick") is not None else "trial"),
            dt_s=first.get("dt_s"),
            extra=extra,
        )
