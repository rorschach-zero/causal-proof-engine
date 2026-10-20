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

# Every standard-library network client and server, the common third-party clients, and the process facilities.
FORBIDDEN_MODULES: frozenset[str] = frozenset({
    "socket", "ssl", "http", "urllib", "urllib3", "requests", "httpx", "aiohttp", "websocket", "websockets",
    "smtplib", "smtpd", "ftplib", "poplib", "imaplib", "nntplib", "telnetlib", "xmlrpc", "socketserver", "wsgiref",
    "asyncio", "asyncore", "asynchat", "webbrowser", "subprocess", "multiprocessing", "ctypes", "pty",
})
# Process-spawning names of os (os.system, os.popen, os.exec*, os.spawn*, os.fork*, os.posix_spawn*).
FORBIDDEN_OS_NAMES: frozenset[str] = frozenset({
    "system", "popen", "fork", "forkpty", "startfile", "posix_spawn", "posix_spawnp",
    "execl", "execle", "execlp", "execlpe", "execv", "execve", "execvp", "execvpe",
    "spawnl", "spawnle", "spawnlp", "spawnlpe", "spawnv", "spawnve", "spawnvp", "spawnvpe",
})
EXECUTOR_PACKAGE = "cpe.executor"
EVIDENCE_PACKAGE = "research"


def _root(name: str) -> str:
    return name.split(".", 1)[0]


def module_name(path: Path, package_root: Path) -> str:
    parts = path.relative_to(package_root.parent).with_suffix("").parts
    if parts[-1] == "__init__":
        parts = parts[:-1]
    return ".".join(parts)


def _resolve_relative(module: str, level: int, base: str | None, is_package: bool) -> str | None:
    """Resolve ``from ..x import y`` against the importing module; None when it escapes the package."""
    anchor = module.split(".") if is_package else module.split(".")[:-1]
    if level - 1 > len(anchor):
        return None
    prefix = anchor[: len(anchor) - (level - 1)]
    return ".".join(prefix + ([base] if base else []))


def imported_names(tree: ast.AST, module: str, is_package: bool) -> list[tuple[str, int]]:
    """Every imported target as a full dotted name: ``import a.b``, ``from a import b`` (as ``a.b``), relative
    forms resolved against the importing module."""
    names: list[tuple[str, int]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.extend((alias.name, node.lineno) for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            if node.level == 0:
                base = node.module
            else:
                base = _resolve_relative(module, node.level, node.module, is_package)
                if base is None:
                    continue
            if base:
                names.append((base, node.lineno))
            names.extend((f"{base}.{alias.name}" if base else alias.name, node.lineno) for alias in node.names)
    return names


def process_api_uses(tree: ast.AST) -> list[tuple[str, int]]:
    """``os.system(...)`` style attribute uses of the process-spawning names of ``os``."""
    uses: list[tuple[str, int]] = []
    for node in ast.walk(tree):
        if (isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name) and node.value.id == "os"
                and node.attr in FORBIDDEN_OS_NAMES):
            uses.append((f"os.{node.attr}", node.lineno))
    return uses


def findings_for_module(path: Path, source: str, package_root: Path) -> list[str]:
    module = module_name(path, package_root)
    is_package = path.name == "__init__.py"
    inside_executor = module == EXECUTOR_PACKAGE or module.startswith(EXECUTOR_PACKAGE + ".")
    tree = ast.parse(source, filename=str(path))
    findings: dict[tuple[int, str], str] = {}  # one finding per line and rule, whatever the import form

    def add(line: int, rule: str, text: str) -> None:
        findings.setdefault((line, rule), f"{path}:{line}: {text}")

    for name, line in imported_names(tree, module, is_package):
        if _root(name) in FORBIDDEN_MODULES:
            add(line, "network", f"imports {name}, a network or process facility outside the offline boundary")
        if _root(name) == "os" and name.split(".")[-1] in FORBIDDEN_OS_NAMES and name.count(".") == 1:
            add(line, "process", f"imports {name}, a process-spawning facility outside the offline boundary")
        if (name == EXECUTOR_PACKAGE or name.startswith(EXECUTOR_PACKAGE + ".")) and not inside_executor:
            add(line, "executor", f"research module imports the executor package {name}")
        if _root(name) == EVIDENCE_PACKAGE:
            add(line, "evidence", f"imports the evidence scripts {name}")
    for name, line in process_api_uses(tree):
        add(line, "process-use", f"uses {name}, a process-spawning facility outside the offline boundary")
    return [findings[key] for key in sorted(findings)]


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
