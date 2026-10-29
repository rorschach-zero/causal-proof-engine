"""Seed derivation for a calibration record (RC-187, RC-304; ``18`` M-1 (i)).

s = SHA-256(canonical bytes of the anchored record ‖ v), with v the verified output of a public beacon round
named in the record and published after the record's anchor. The seed is computed here from those two inputs
only, so that no party can choose it; a seed supplied by a party is refused by the registry.
"""
from __future__ import annotations

import hashlib

from cpe.canonical import JsonValue, canonical_bytes


def derive_seed(record_payload: JsonValue, beacon_value: str) -> str:
    return hashlib.sha256(canonical_bytes(record_payload) + beacon_value.encode("ascii")).hexdigest()
