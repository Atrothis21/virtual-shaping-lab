"""Canonical V3.9 operator pipeline namespace."""

from __future__ import annotations

from virtual_shaping_lab.vsl._migration import suppress_deprecation_for

with suppress_deprecation_for("virtual_shaping_lab.vsl.operator.pipeline"):
    from virtual_shaping_lab.vsl.operator.pipeline import *  # noqa: F401,F403

