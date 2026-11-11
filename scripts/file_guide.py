"""Maintain a complete tracked-file README purpose inventory; unknown file types fail closed. Created by Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# variable: ROOT — line 32
# variable: BEGIN — line 33
# variable: END — line 33
# variable: SPECIAL — line 34
# definition: purpose — line 58
# parameter: path — line 58
# variable: source — line 62
# variable: line — line 70
# definition: main — line 76
# variable: parser — line 78
# variable: args — line 80
# variable: files — line 81
# variable: rows — line 89
# variable: path — line 90
# variable: label — line 91
# variable: readme — line 93
# variable: original — line 94
# variable: end — line 95
# variable: start — line 95
# variable: expected — line 96
# END CODE MAP

from __future__ import annotations

import argparse
import ast
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BEGIN, END = "<!-- BEGIN FILE GUIDE -->", "<!-- END FILE GUIDE -->"
SPECIAL = {
    "requirements-native.lock": "Exact complete hash-locked native freezing tool graph; no runtime setup dependency.",
    "docs/reports/project-guide.docx": "Reviewed Word project guide bound to the documented source revision.",
    "docs/reports/publications.json": "Exact Office digests, visual review scopes and immutable source baselines.",
    "patches/disable-unused-okta-mfa.patch": "Reviewed hash-bound upstream lab patch: unsupported Okta login MFA always rejects, removing obsolete SDK linkage; actual Go regression included.",
    ".gitignore": "Keep generated keys, credentials, logs, tools and working data untracked.",
    ".gitattributes": "Consistent LF source checkout across operating systems.",
    ".dockerignore": "Allow only Dockerfile and reviewed startup script into the image build.",
    "LICENSE": "MIT terms for authored source; upstream tools retain their licenses.",
    "pyproject.toml": "Strict lint/type/test/statement-and-branch coverage configuration.",
    "tools.lock.json": "Exact official release hashes and immutable PostgreSQL base image.",
    "requirements-dev.in": "Exact portable development tool inputs.",
    "requirements-dev.lock": "Complete hash-locked portable development graph.",
    "requirements-integration.in": "Exact live-only PostgreSQL driver input.",
    "requirements-integration.lock": "Hash-locked CPython3.14/Linux-x86_64 live-only driver graph.",
    "docs/reports/benchmark.json": "Actual warmed broker benchmark with a one-issuance oracle.",
    "docs/reports/live.json": "Selected actual service case durations and safe lifecycle counters.",
    "docs/reports/live.html": "Inert HTML rendering of the selected actual service aggregate.",
    "docs/reports/simulation.json": "Explicitly simulated offline assertions and virtual elapsed times.",
    "docs/reports/simulation.html": "Inert HTML rendering of the clearly labeled offline simulation.",
    "docs/reports/ci.json": "Immutable executable-source acceptance snapshot with actual completed checks.",
}


def purpose(path: str) -> str:
    """Require a human-readable purpose for every tracked file, not a generic guessed fallback."""
    if path in SPECIAL:
        return SPECIAL[path]
    source = (ROOT / path).read_text(encoding="utf-8")
    if path.endswith(".py"):
        return (ast.get_docstring(ast.parse(source)) or "").splitlines()[0]
    if path.endswith(".md"):
        return source.splitlines()[0].lstrip("# ") + "."
    if path.endswith((".yml", ".sh", ".hcl", ".sql")) or path == "Dockerfile":
        return next(
            line.lstrip("#- ")
            for line in source.splitlines()
            if line.startswith(("# ", "-- "))
        )
    raise ValueError("tracked-file purpose missing")


def main() -> int:
    """Generate/check exact tracked-file summaries; stage intended files before regeneration."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    files = (
        subprocess.check_output(["git", "ls-files", "-z"], cwd=ROOT)
        .decode()
        .rstrip("\0")
        .split("\0")
    )
    if files == [""]:
        raise ValueError("stage intended files first")
    rows = ["| File | Purpose |", "| --- | --- |"]
    for path in sorted(files):
        label = path.replace("_", "\\_")
        rows.append(f"| [{label}]({path}) | {purpose(path).replace('|', '/')} |")
    readme = ROOT / "README.md"
    original = readme.read_text(encoding="utf-8")
    start, end = original.index(BEGIN) + len(BEGIN), original.index(END)
    expected = original[:start] + "\n\n" + "\n".join(rows) + "\n\n" + original[end:]
    if args.check and original != expected:
        raise ValueError("README file guide stale")
    if not args.check:
        readme.write_text(expected, encoding="utf-8", newline="\n")
    print(f"README inventory current: {len(files)} files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
