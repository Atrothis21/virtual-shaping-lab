"""Canonical V3.9 spec binding namespace."""

from __future__ import annotations

from virtual_shaping_lab.vsl._migration import suppress_deprecation_for

with suppress_deprecation_for("virtual_shaping_lab.vsl.spec.binding"):
    from virtual_shaping_lab.vsl.spec.binding import *  # noqa: F401,F403

