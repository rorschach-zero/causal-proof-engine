"""Provenance check of commits and pull-request text (``17`` T-09; ``AGENTS.md`` section 7).

Three checks, provider-neutral:

1. Text: every commit message in the range, and the pull-request title and body when given, must carry no AI
   attribution trailer, tool session link or promotional footer, from any tool.
2. Identity: every commit in the range has an author and a committer on the designated list (``AGENTS.md``
   section 7, recorded on issue #3 comment 6300164338; a text check cannot see metadata, RC-81); GitHub's own
   committer identity passes only on a two-parent commit whose author is designated.
3. Labels: a message that names a reconciliation round, a matrix version or a specification version must name
   the ones its tree carries (RC-277). The pull-request title and body are checked against the head tree before
   the merge; after it, every commit the merge added is checked against its own tree, whether it has one parent
   (squash, rebase) or two (merge commit) (RC-279).

Usage: ``python tools/check_provenance.py --range <base>..<head> [--title-file F] [--body-file F]``.
Exit status 0 when clean, 1 on any finding (each printed), 2 on a usage error.
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

# Designated identities, as the owner recorded them on issue #3, comment 6300164338 (OD9b, partial record): one
# person under two display names and one address as author and committer; GitHub's committer identity only on a
# commit with two parents whose author is designated (a merge made through GitHub).
DESIGNATED_AUTHORS: frozenset[str] = frozenset({"Salah Aouaj <salah@hydeout.ch>", "rorschach0 <salah@hydeout.ch>"})
DESIGNATED_COMMITTERS: frozenset[str] = DESIGNATED_AUTHORS
GITHUB_MERGE_COMMITTER = "GitHub <noreply@github.com>"

# Provider-neutral: every git-style trailer except the owner-requested human ``Reviewed-by:`` line (``AGENTS.md``
# section 7), session links, promotional footers of any assistant (a line that opens with "Generated with/by",
# or one naming a known assistant anywhere), tool identities and badges; all case-insensitive.
PROHIBITED_PATTERNS: tuple[tuple[str, str], ...] = (
    ("attribution trailer", r"(?i)^\s*(?!reviewed-by:)[a-z][a-z0-9]*(?:-[a-z0-9]+)*-by:\s*\S"),
    ("session link", r"(?i)(claude\.ai/code/session|chatgpt\.com/codex/tasks|Claude-Session:)"),
    ("promotional footer", r"(?i)^[\s_*]*generated (with|by)\b"),
    ("promotional footer", r"(?i)generated (with|by)\b.*\b(claude|codex|copilot|chatgpt|openai|anthropic|gemini|cursor|devin|aider)\b"),
    ("tool identity", r"(?i)(noreply@anthropic\.com|noreply@openai\.com|users\.noreply\.github\.com.*\b(claude|codex|copilot)\b)"),
    ("assistant emoji badge", "🤖"),
)

# "round 50" and "rounds 1–50" both name round 50 (the last of a range). A round is a reconciliation label only
# in that context: the word "reconciliation" on the same line, or a matrix or specification label in the message;
# "Address review round 2" names no document version.
ROUND_PATTERN = re.compile(r"\brounds? (?:\d+\s*(?:–|-|to)\s*)?(\d+)\b", re.IGNORECASE)
RECONCILIATION_LINE = re.compile(r"(?i)\breconciliation\b.*\brounds? ")
MATRIX_PATTERN = re.compile(r"\bmatrix v(\d+)\b", re.IGNORECASE)
SPEC_PATTERN = re.compile(r"\bspecification (?:v|version )(\d+)\b", re.IGNORECASE)

# The label positions of the research documents, as research/reproduction/check_appendix_scripts.py reads them.
MATRIX_LABEL = re.compile(r"^\*\*Version:\*\* v(\d+), [-\d]+\. \*\*Round:\*\* (\d+) ", re.MULTILINE)
SPEC_LABEL = re.compile(r"^version (\d+) \(round (\d+):", re.MULTILINE)
MATRIX_PATH = "research/16-reconciliation-matrix.md"
SPEC_PATH = "research/17-phase1-amended-specification.md"


@dataclass(frozen=True)
class Commit:
    sha: str
    author: str
    committer: str
    message: str
    parents: tuple[str, ...]


@dataclass(frozen=True)
class TreeLabels:
    matrix_version: int | None
    matrix_round: int | None
    spec_version: int | None
    spec_round: int | None


def git(*args: str, repo: Path) -> str:
    return subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True, text=True).stdout


def commits_in_range(commit_range: str, repo: Path) -> list[Commit]:
    separator = "\x1e"
    out = git("log", "--format=%H%x1f%an <%ae>%x1f%cn <%ce>%x1f%P%x1f%B" + separator, commit_range, repo=repo)
    commits = []
    for chunk in out.split(separator):
        if not chunk.strip():
            continue
        sha, author, committer, parents, message = chunk.lstrip("\n").split("\x1f", 4)
        commits.append(Commit(sha, author, committer, message.strip("\n"), tuple(parents.split())))
    return commits


def text_findings(text: str, where: str) -> list[str]:
    findings = []
    for label, pattern in PROHIBITED_PATTERNS:
        for match in re.finditer(pattern, text, flags=re.MULTILINE):
            line = text.count("\n", 0, match.start()) + 1
            findings.append(f"{where}: {label} at line {line}: {match.group(0).strip()!r}")
    return findings


def identity_findings(commit: Commit, authors: frozenset[str] = DESIGNATED_AUTHORS,
                      committers: frozenset[str] = DESIGNATED_COMMITTERS) -> list[str]:
    findings = []
    author_designated = commit.author in authors
    if not author_designated:
        findings.append(f"commit {commit.sha[:10]}: author {commit.author!r} is not a designated identity")
    github_merge = commit.committer == GITHUB_MERGE_COMMITTER and len(commit.parents) == 2 and author_designated
    if commit.committer not in committers and not github_merge:
        findings.append(f"commit {commit.sha[:10]}: committer {commit.committer!r} is not a designated identity")
    return findings


def _label(pattern: re.Pattern[str], text: str | None) -> tuple[int | None, int | None]:
    if text is None:
        return None, None
    matches = pattern.findall(text)
    if len(matches) != 1:
        return None, None
    return int(matches[0][0]), int(matches[0][1])


def tree_labels_from_texts(matrix: str | None, spec: str | None) -> TreeLabels:
    matrix_version, matrix_round = _label(MATRIX_LABEL, matrix)
    spec_version, spec_round = _label(SPEC_LABEL, spec)
    return TreeLabels(matrix_version, matrix_round, spec_version, spec_round)


def tree_labels(tree: str, repo: Path) -> TreeLabels:
    def read(path: str) -> str | None:
        try:
            return git("show", f"{tree}:{path}", repo=repo)
        except subprocess.CalledProcessError:
            return None

    return tree_labels_from_texts(read(MATRIX_PATH), read(SPEC_PATH))


def label_findings(message: str, labels: TreeLabels, where: str) -> list[str]:
    """A message that names a round, matrix version or specification version must name the tree's (RC-277)."""
    findings = []
    names_document = bool(MATRIX_PATTERN.search(message) or SPEC_PATTERN.search(message))
    for name, pattern, expected in (
        ("round", ROUND_PATTERN, labels.matrix_round),
        ("matrix version", MATRIX_PATTERN, labels.matrix_version),
        ("specification version", SPEC_PATTERN, labels.spec_version),
    ):
        for match in pattern.finditer(message):
            if name == "round" and not names_document:
                line = message[message.rfind("\n", 0, match.start()) + 1:message.find("\n", match.end()) % (len(message) + 1)]
                if not RECONCILIATION_LINE.search(line):
                    continue
            named = int(match.group(1))
            if expected is None:
                findings.append(f"{where}: names {name} {named} but the tree carries no such label")
            elif named != expected:
                findings.append(f"{where}: names {name} {named}, the tree carries {expected}")
    return findings


def check(commit_range: str, repo: Path, title: str | None, body: str | None, head: str) -> list[str]:
    findings: list[str] = []
    commits = commits_in_range(commit_range, repo)
    for commit in commits:
        where = f"commit {commit.sha[:10]}"
        findings += text_findings(commit.message, where)
        findings += identity_findings(commit)
        findings += label_findings(commit.message, tree_labels(commit.sha, repo), where)
    if title is not None or body is not None:
        prospective = "\n\n".join(part for part in (title, body) if part)
        findings += text_findings(prospective, "pull request text")
        findings += label_findings(prospective, tree_labels(head, repo), "pull request text")
    return findings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n", maxsplit=1)[0])
    parser.add_argument("--range", required=True, help="git revision range, for example origin/main..HEAD")
    parser.add_argument("--repo", default=".", help="repository path")
    parser.add_argument("--title-file", help="file holding the pull-request title (prospective merge message)")
    parser.add_argument("--body-file", help="file holding the pull-request body")
    parser.add_argument("--head", default="HEAD", help="tree the pull-request text is checked against")
    args = parser.parse_args(argv)
    repo = Path(args.repo)
    title = Path(args.title_file).read_text(encoding="utf-8") if args.title_file else None
    body = Path(args.body_file).read_text(encoding="utf-8") if args.body_file else None
    try:
        findings = check(args.range, repo, title, body, args.head)
    except subprocess.CalledProcessError as error:
        print(f"git failed: {error.stderr.strip()}", file=sys.stderr)
        return 2
    for finding in findings:
        print(finding)
    print(f"provenance check: {len(findings)} finding(s) over {args.range}")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
