"""Canonical V3.9 rollout episode namespace."""

from __future__ import annotations

from virtual_shaping_lab.vsl._migration import suppress_deprecation_for

with suppress_deprecation_for("virtual_shaping_lab.vsl.environment.episode"):
    from virtual_shaping_lab.vsl.environment.episode import *  # noqa: F401,F403

