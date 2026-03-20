"""Canonical V3.9 learner validation namespace."""

from __future__ import annotations

from virtual_shaping_lab.vsl._migration import suppress_deprecation_for

with suppress_deprecation_for("virtual_shaping_lab.vsl.agent.learning.validator"):
    from virtual_shaping_lab.vsl.agent.learning.validator import *  # noqa: F401,F403

