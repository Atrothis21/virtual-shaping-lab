"""Canonical V3.9 temporal-basis namespace."""

from __future__ import annotations

from virtual_shaping_lab.vsl._migration import suppress_deprecation_for

with suppress_deprecation_for("virtual_shaping_lab.vsl.agent.representation.temporal"):
    from virtual_shaping_lab.vsl.agent.representation.temporal import *  # noqa: F401,F403

