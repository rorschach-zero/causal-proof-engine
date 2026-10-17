#!/usr/bin/env python3
"""Check that a Graphify response describes the exact authorized code revision.

This checks provenance only, never code correctness or test coverage.
No network access, dependencies, credentials, or Graphify writes are needed.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

FULL_SHA = re.compile(r"[0-9a-f]{40}\Z")


def assess(response: Any, expected_sha: str, repository_id: str) -> tuple[bool, str]:
    """Fail closed on missing, wrong-repository, or non-exact graph revisions."""
    if not FULL_SHA.fullmatch(expected_sha):
        return False, "INVALID_EXPECTED_SHA"
    if not repository_id.strip():
        return False, "INVALID_REPOSITORY_ID"
    if not isinstance(response, dict):
        return False, "INVALID_RESPONSE"
    if response.get("repositoryId") != repository_id:
        return False, "REPOSITORY_MISMATCH"
    indexed_sha = response.get("commitSha")
    if not isinstance(indexed_sha, str) or not FULL_SHA.fullmatch(indexed_sha):
        return False, "MISSING_OR_INVALID_INDEX_SHA"
    if indexed_sha != expected_sha:
        return False, "STALE_INDEX"
    return True, "EXACT_INDEX_SHA_MATCH"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--response", type=Path, required=True, help="Saved Graphify graph_stats or query_graph JSON response")
    parser.add_argument("--expected-sha", required=True, help="Exact 40-character GitHub PR head commit SHA")
    parser.add_argument("--repository-id", required=True, help="Graphify repository UUID from list_repositories")
    args = parser.parse_args()

    try:
        response = json.loads(args.response.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        print(f"GRAPHIFY_SNAPSHOT_UNUSABLE: {type(exc).__name__}")
        return 2

    matched, reason = assess(response, args.expected_sha, args.repository_id)
    print(f"GRAPHIFY_{reason}: {'exact revision only; not proof of completeness' if matched else 'context only; use current GitHub source and diff'}")
    return 0 if matched else 2


if __name__ == "__main__":
    raise SystemExit(main())
