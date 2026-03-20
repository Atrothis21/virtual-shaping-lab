"""Canonical V3.9 replay harness namespace."""

from __future__ import annotations

from virtual_shaping_lab.vsl._migration import suppress_deprecation_for

with suppress_deprecation_for("virtual_shaping_lab.vsl.rollout.replay"):
    from virtual_shaping_lab.vsl.rollout.replay import *  # noqa: F401,F403

