"""Canonical V3.9 learner-boundary resolution namespace."""

from __future__ import annotations

from virtual_shaping_lab.vsl._migration import suppress_deprecation_for

with suppress_deprecation_for("virtual_shaping_lab.vsl.agent.learning.boundary"):
    from virtual_shaping_lab.vsl.agent.learning.boundary import *  # noqa: F401,F403

