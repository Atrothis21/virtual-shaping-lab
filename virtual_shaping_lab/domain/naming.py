"""Shared naming/normalization helpers for stable registry lookups."""

from __future__ import annotations


def normalize_protocol_key(name: str) -> str:
    return str(name).strip().lower().replace("-", "_")

