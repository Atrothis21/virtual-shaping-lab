"""Canonical V3.9 rollout trial-state namespace."""

from __future__ import annotations

from virtual_shaping_lab.vsl._migration import suppress_deprecation_for

with suppress_deprecation_for("virtual_shaping_lab.vsl.environment.trial_state"):
    from virtual_shaping_lab.vsl.environment.trial_state import *  # noqa: F401,F403

