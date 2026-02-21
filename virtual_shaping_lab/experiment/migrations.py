from __future__ import annotations

from copy import deepcopy
from typing import Dict, Any


CURRENT_SCHEMA_VERSION = "1.2"
SUPPORTED_SCHEMA_VERSIONS = {"1.0", "1.1", "1.2"}


def migrate_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Upgrade older payloads to the current schema version.
    The migration is intentionally minimal and only normalizes versioning.
    """
    if not isinstance(payload, dict):
        raise ValueError("payload must be an object")

    data = deepcopy(payload)
    exp = data.get("experiment")
    if not isinstance(exp, dict):
        raise ValueError("payload.experiment must be an object")

    version = exp.get("schema_version")
    if version is None:
        version = "1.1"

    if version not in SUPPORTED_SCHEMA_VERSIONS:
        raise ValueError(
            f"Unsupported schema_version '{version}'. "
            f"Supported: {', '.join(sorted(SUPPORTED_SCHEMA_VERSIONS))}"
        )

    # Current migrations are no-ops beyond version normalization.
    exp["schema_version"] = CURRENT_SCHEMA_VERSION
    data["experiment"] = exp
    return data
