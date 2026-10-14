"""Allowlisted aggregate reports, inert escaped HTML and new-directory-only output. Created by Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# variable: CASES — line 38
# variable: COUNTERS — line 67
# definition: validate — line 70
# parameter: value — line 70
# variable: cases — line 89
# variable: names — line 92
# variable: case — line 93
# variable: metrics — line 106
# variable: v — line 110
# definition: read_report — line 116
# parameter: path — line 116
# definition: render — line 127
# parameter: report — line 127
# variable: value — line 129
# variable: rows — line 130
# variable: c — line 132
# definition: write_report — line 147
# parameter: destination — line 147
# parameter: report — line 147
# variable: value — line 149
# variable: absolute — line 150
# variable: p — line 151
# END CODE MAP

from __future__ import annotations

import html
import json
import re
from pathlib import Path
from typing import Any

from rotation.bao import invalid_constant, unique
from rotation.contracts import number

CASES = {
    "simulation": {
        "cache",
        "rotation",
        "retry",
        "grace",
        "expiry",
        "denied",
        "stale_invalidation",
        "redaction",
    },
    "live": {
        "tls",
        "bootstrap",
        "acl",
        "readonly",
        "renewal",
        "overlap",
        "revocation",
        "expiry",
        "root_rotation",
        "outage_grace",
        "outage_expiry",
        "recovery",
        "identity_revocation",
        "redaction",
        "cleanup",
    },
}
COUNTERS = {"requests", "issues", "attempts", "fallbacks", "denials", "invalidations"}


def validate(value: Any) -> dict[str, Any]:
    """Require exact report fields/cases and bounded counters; secret/unexpected metadata is rejected, not redacted heuristically."""
    if not isinstance(value, dict) or set(value) != {
        "schema",
        "mode",
        "source_sha",
        "cases",
        "metrics",
    }:
        raise ValueError("report fields invalid")
    if (
        type(value["schema"]) is not int
        or value["schema"] != 1
        or not isinstance(value["mode"], str)
        or value["mode"] not in CASES
        or not isinstance(value["source_sha"], str)
        or not re.fullmatch(r"[a-f0-9]{40}", value["source_sha"])
    ):
        raise ValueError("report identity invalid")
    cases = value["cases"]
    if not isinstance(cases, list) or len(cases) != len(CASES[value["mode"]]):
        raise ValueError("case set invalid")
    names = set()
    for case in cases:
        if (
            not isinstance(case, dict)
            or set(case) != {"name", "passed", "duration_ms"}
            or not isinstance(case["name"], str)
            or case["name"] not in CASES[value["mode"]]
            or type(case["passed"]) is not bool
        ):
            raise ValueError("case fields invalid")
        names.add(case["name"])
        number(case["duration_ms"], 0, 900000)
    if names != CASES[value["mode"]]:
        raise ValueError("duplicate/missing cases")
    metrics = value["metrics"]
    if (
        not isinstance(metrics, dict)
        or set(metrics) != COUNTERS
        or any(type(v) is not int or not 0 <= v <= 1000000 for v in metrics.values())
    ):
        raise ValueError("counter fields invalid")
    return value


def read_report(path: Path) -> dict[str, Any]:
    """Read a bounded regular non-symlink aggregate; reject ambiguous/nonfinite JSON."""
    if path.is_symlink() or not path.is_file() or path.stat().st_size > 65536:
        raise ValueError("report file invalid")
    return validate(
        json.loads(
            path.read_bytes(), object_pairs_hook=unique, parse_constant=invalid_constant
        )
    )


def render(report: dict[str, Any]) -> str:
    """Render validated aggregate only: no scripts, forms, remote assets, passwords or raw provider errors."""
    value = validate(report)
    rows = "".join(
        f"<tr><td>{html.escape(c['name'])}</td><td>{'PASS' if c['passed'] else 'FAIL'}</td><td>{c['duration_ms']:.3f}</td></tr>"
        for c in value["cases"]
    )
    return (
        '<!doctype html><html lang="en"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        "<meta http-equiv=\"Content-Security-Policy\" content=\"default-src 'none'; style-src 'unsafe-inline'; base-uri 'none'; form-action 'none'\">"
        "<title>Secret rotation reliability — Jason Stys</title><style>body{font:16px system-ui;max-width:960px;margin:2rem auto;padding:1rem;background:#101c2b;color:#e8f0fa}table{width:100%;border-collapse:collapse}td,th{padding:.7rem;text-align:left;border-bottom:1px solid #52708d}code{overflow-wrap:anywhere}a{color:#72d8cd}</style></head><body>"
        f"<h1>Secret rotation reliability lab</h1><p>Created by Jason Stys · {html.escape(value['mode'])} evidence</p>"
        f"<p>Source: <code>{value['source_sha']}</code>. These are measured exercise results, not a production SLA or certification.</p>"
        '<table><caption>Credential lifecycle cases</caption><thead><tr><th scope="col">Case</th><th scope="col">Outcome</th><th scope="col">Duration (ms)</th></tr></thead><tbody>'
        + rows
        + '</tbody></table><p>Contact: <a href="https://github.com/JasonStys">JasonStys on GitHub</a>.</p></body></html>'
    )


def write_report(report: dict[str, Any], destination: Path) -> None:
    """Create a new output directory after validating all data; never overwrite an existing report or follow a symlink parent."""
    value = validate(report)
    absolute = destination.absolute()
    if any(p.is_symlink() for p in [absolute, *absolute.parents]):
        raise ValueError("symlink output refused")
    absolute.mkdir(parents=True, exist_ok=False, mode=0o700)
    (absolute / "report.json").write_text(
        json.dumps(value, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    (absolute / "report.html").write_text(render(value), encoding="utf-8", newline="\n")
