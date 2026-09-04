from __future__ import annotations

import uuid

# Stable namespace derived once from:
# https://github.com/ImanNasrEsfahani/grammar-mastery-advanced/ADV/v1
ADV_UUID_NAMESPACE = uuid.UUID("2ff38ec0-7fd9-5f16-9864-8976e9a7ac06")


def stable_uuid(kind: str, canonical_id: str) -> str:
    """Map a canonical ADV string ID to a deterministic physical UUID.

    Canonical IDs remain unchanged in source files. This function exists only at
    the repository/database boundary.
    """
    kind = str(kind).strip().lower()
    canonical_id = str(canonical_id).strip()
    if not kind or not canonical_id:
        raise ValueError("kind and canonical_id are required")
    return str(uuid.uuid5(ADV_UUID_NAMESPACE, f"{kind}:{canonical_id}"))
