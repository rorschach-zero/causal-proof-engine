"""Static import boundary of the Phase 1 package (``17`` section 3 item 8).

Two rules over every module under ``cpe/``:

1. No module imports a network or process-spawning facility. Phase 1 is offline: the capability model's "no network
   path exists" (item 5) and the handoff's no-execution boundary are checked here statically.
2. No research module imports the executor package: a module outside ``cpe.executor`` never imports
   ``cpe.executor`` (``AGENTS.md`` section 3). No executor exists in Phase 1; the rule is in place before it does.
3. No module under ``cpe/`` imports the evidence scripts of ``research/reproduction``.

The check is useful and not sufficient (dynamic imports are covered by T-32 and T-34); it reports the import, and
the test suite's pass condition never rests on it alone.

Usage: ``python tools/check_import_boundary.py [package_dir]``. Exit 0 when clean, 1 on findings.
"""
from __future__ import annotations

import ast
import sys
from pathlib import Path

FORBIDDEN_MODULES: frozenset[str] = frozenset({
    "socket", "ssl", "http", "urllib", "urllib3", "requests", "httpx", "aiohttp", "websocket", "websockets",
    "smtplib", "ftplib", "telnetlib", "xmlrpc", "asyncio", "subprocess", "multiprocessing", "ctypes",
})
EXECUTOR_PACKAGE = "cpe.executor"
EVIDENCE_PACKAGE = "research"


def _root(name: str) -> str:
    return name.split(".", 1)[0]


def imported_names(tree: ast.AST) -> list[tuple[str, int]]:
    names: list[tuple[str, int]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.extend((alias.name, node.lineno) for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
            names.append((node.module, node.lineno))
    return names


def findings_for_module(path: Path, source: str, package_root: Path) -> list[str]:
    module = ".".join(path.relative_to(package_root.parent).with_suffix("").parts)
    inside_executor = module == EXECUTOR_PACKAGE or module.startswith(EXECUTOR_PACKAGE + ".")
    findings = []
    for name, line in imported_names(ast.parse(source, filename=str(path))):
        if _root(name) in FORBIDDEN_MODULES:
            findings.append(f"{path}:{line}: imports {name}, a network or process facility outside the offline boundary")
        if (name == EXECUTOR_PACKAGE or name.startswith(EXECUTOR_PACKAGE + ".")) and not inside_executor:
            findings.append(f"{path}:{line}: research module imports the executor package {name}")
        if _root(name) == EVIDENCE_PACKAGE:
            findings.append(f"{path}:{line}: imports the evidence scripts {name}")
    return findings


def check_package(package_root: Path) -> list[str]:
    findings: list[str] = []
    for path in sorted(package_root.rglob("*.py")):
        findings += findings_for_module(path, path.read_text(encoding="utf-8"), package_root)
    return findings


def main(argv: list[str] | None = None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    package_root = Path(args[0]) if args else Path("cpe")
    findings = check_package(package_root)
    for finding in findings:
        print(finding)
    print(f"import boundary: {len(findings)} finding(s) under {package_root}")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
