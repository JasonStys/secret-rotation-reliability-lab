"""Offline demo and strict aggregate inspection CLI; raw secrets/errors never printed. Created by Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# definition: main — line 26
# variable: parser — line 28
# variable: commands — line 29
# variable: demo — line 30
# variable: report — line 34
# variable: args — line 38
# variable: sha — line 41
# variable: value — line 47
# variable: value — line 50
# variable: case — line 51
# variable: passed — line 51
# END CODE MAP

from __future__ import annotations

import argparse
import subprocess
from pathlib import Path

from rotation.evidence import read_report, write_report
from rotation.simulation import simulate


def main() -> int:
    """Choose a new-directory-only simulated demo or inspect existing aggregate; return nonzero on failed cases."""
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    demo = commands.add_parser(
        "demo", help="Offline deterministic simulation; no Docker/OpenBao/data access"
    )
    demo.add_argument("--output", type=Path, required=True)
    report = commands.add_parser(
        "report", help="Validate a bounded aggregate, not arbitrary logs or credentials"
    )
    report.add_argument("path", type=Path)
    args = parser.parse_args()
    try:
        if args.command == "demo":
            sha = subprocess.check_output(
                ["git", "rev-parse", "HEAD"],
                cwd=Path(__file__).resolve().parents[1],
                text=True,
                timeout=5,
            ).strip()
            value = simulate(sha)
            write_report(value, args.output)
        else:
            value = read_report(args.path)
        passed = sum(case["passed"] for case in value["cases"])
        print(
            f"{value['mode']}: {passed}/{len(value['cases'])} cases pass — Jason Stys"
        )
        return 0 if passed == len(value["cases"]) else 1
    except (OSError, ValueError, subprocess.SubprocessError):
        print(
            "Operation refused; check input/output and Git source identity. No raw input or credentials logged."
        )
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
