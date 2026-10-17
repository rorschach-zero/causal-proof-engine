"""Fail-closed check for embedded credentials in versioned MCP client configuration.

No network, external dependencies, token values in logs, or assumptions that this
replaces a repository-wide secret scanner.  Rejects credential-bearing configuration
KEYS and explicit auth-value prefixes, rather than a brittle substring checklist.
"""
from __future__ import annotations

import argparse
import json
import re
import tomllib
from pathlib import Path
from typing import Any

DEFAULT_CONFIGS = (
    ".mcp.json",
    ".codex/config.toml",
    ".gemini/settings.json",
)

SENSITIVE_PARTS = frozenset({
    "key", "token", "secret", "password", "passwd", "credential",
    "credentials", "authorization", "auth", "bearer",
})
EMBEDDED_AUTH = re.compile(r"^\s*(?:bearer|basic)\s+\S+", re.IGNORECASE)


def normalize_key(key: str) -> str:
    camel = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", key)
    return re.sub(r"[^a-z0-9]+", "_", camel.lower()).strip("_")


def sensitive_key(key: str) -> bool:
    """Conservatively deny named credential/key fields in any nested map."""
    normalized = normalize_key(key)
    return bool(SENSITIVE_PARTS.intersection(normalized.split("_")))


def credential_paths(value: Any, prefix: str = "$") -> list[str]:
    """Return only offending field paths; never leak secret values."""
    findings: list[str] = []
    if isinstance(value, dict):
        for key, item in value.items():
            if not isinstance(key, str):
                findings.append(f"{prefix}.<non-string-key>")
                continue
            path = f"{prefix}.{key}"
            if sensitive_key(key):
                findings.append(path)
            findings.extend(credential_paths(item, path))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            findings.extend(credential_paths(item, f"{prefix}[{index}]"))
    elif isinstance(value, str) and EMBEDDED_AUTH.match(value):
        findings.append(prefix)
    return findings


def scan_file(path: Path) -> tuple[bool, list[str]]:
    """Parse JSON/TOML or fail closed. Reject broker endpoints in MCP config."""
    try:
        raw = path.read_text(encoding="utf-8")
        if path.suffix == ".toml":
            payload: Any = tomllib.loads(raw)
        elif path.suffix == ".json":
            payload = json.loads(raw)
        else:
            return False, [f"{path}: unsupported format"]
    except (OSError, UnicodeError, ValueError) as exc:
        return False, [f"{path}: unreadable configuration ({type(exc).__name__})"]
    if not isinstance(payload, dict):
        return False, [f"{path}: expected configuration object"]

    findings = credential_paths(payload)
    if "saxobank.com" in raw.lower():
        findings.append("$: Saxo endpoint not permitted in developer MCP config")
    return not findings, findings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("."))
    args = parser.parse_args()

    rejected = False
    for relative in DEFAULT_CONFIGS:
        path = args.root / relative
        ok, findings = scan_file(path)
        if not ok:
            rejected = True
            for finding in findings:
                print(f"MCP_CONFIG_REJECTED: {relative}: {finding}")
        else:
            print(f"MCP_CONFIG_OK: {relative}")
    return 2 if rejected else 0


if __name__ == "__main__":
    raise SystemExit(main())
