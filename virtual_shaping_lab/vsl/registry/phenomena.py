"""Canonical V3.9 phenomenon registry namespace."""

from __future__ import annotations

from virtual_shaping_lab.vsl._migration import suppress_deprecation_for

with suppress_deprecation_for("virtual_shaping_lab.vsl.registry.phenomenon_registry"):
    from virtual_shaping_lab.vsl.registry.phenomenon_registry import *  # noqa: F401,F403

