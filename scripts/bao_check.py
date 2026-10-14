"""Scan the actual verified OpenBao binary's Go module inventory with no advisory exclusions. Created by Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# variable: ROOT — line 32
# definition: main — line 35
# variable: source — line 37
# variable: directory — line 38
# variable: report — line 41
# variable: process — line 42
# variable: value — line 62
# variable: results — line 63
# variable: result — line 65
# variable: findings — line 68
# variable: key — line 71
# variable: result — line 79
# variable: finding — line 80
# variable: result — line 91
# variable: result — line 92
# variable: result — line 102
# variable: receipt — line 108
# variable: result — line 113
# END CODE MAP

from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    """Copy only the pinned installed binary to a unique ignored directory; enforce HIGH/CRITICAL and actual inventory presence."""
    source = ROOT / ".tools/bao"
    directory = ROOT / "out" / ("bao-scan-" + uuid.uuid4().hex)
    directory.mkdir(parents=True, mode=0o700)
    shutil.copy2(source, directory / "bao")
    report = directory / "scan.json"
    process = subprocess.run(
        [
            str(ROOT / ".tools/trivy"),
            "rootfs",
            "--scanners",
            "vuln",
            "--severity",
            "HIGH,CRITICAL",
            "--exit-code",
            "1",
            "--list-all-pkgs",
            "--format",
            "json",
            "--output",
            str(report),
            str(directory),
        ],
        check=False,
        timeout=180,
    )
    value = json.loads(report.read_text(encoding="utf-8"))
    results = [
        result
        for result in value.get("Results", [])
        if result.get("Type") == "gobinary"
    ]
    findings = [
        {
            key: finding.get(key, "")
            for key in (
                "VulnerabilityID",
                "PkgName",
                "Severity",
                "InstalledVersion",
                "FixedVersion",
            )
        }
        for result in results
        for finding in result.get("Vulnerabilities", [])
    ]
    print(
        json.dumps(
            {"go_inventory_files": len(results), "high_critical_findings": findings}
        ),
        flush=True,
    )
    if (
        process.returncode != 0
        or not results
        or not all(result.get("Packages") for result in results)
        or any(result.get("Vulnerabilities") for result in results)
    ):
        raise ValueError("actual OpenBao inventory missing or vulnerable")
    print(
        json.dumps(
            {
                "openbao_binary_sha256": hashlib.sha256(
                    source.read_bytes()
                ).hexdigest(),
                "go_packages_scanned": sum(
                    len(result["Packages"]) for result in results
                ),
                "high_critical": 0,
            }
        )
    )
    receipt = {
        "source_sha": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True, timeout=10
        ).strip(),
        "binary_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "go_packages_scanned": sum(len(result["Packages"]) for result in results),
        "high_critical": 0,
    }
    (ROOT / ".tools/bao-scan.json").write_text(
        json.dumps(receipt, sort_keys=True) + "\n", encoding="utf-8", newline="\n"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
