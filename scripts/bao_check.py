"""Scan the actual verified OpenBao binary's Go module inventory with no advisory exclusions. Created by Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# variable: ROOT — line 25
# definition: main — line 28
# variable: source — line 30
# variable: directory — line 31
# variable: report — line 34
# variable: value — line 55
# variable: results — line 56
# variable: result — line 58
# variable: result — line 63
# variable: result — line 64
# variable: result — line 74
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
    subprocess.run(
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
        check=True,
        timeout=180,
    )
    value = json.loads(report.read_text(encoding="utf-8"))
    results = [
        result
        for result in value.get("Results", [])
        if result.get("Type") == "gobinary"
    ]
    if (
        not results
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
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
