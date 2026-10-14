"""Build pinned upstream OpenBao with reviewed Go/x-net security fixes, never suppressing advisories. Created by Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# variable: ROOT — line 30
# definition: main — line 33
# variable: spec — line 39
# variable: version — line 42
# variable: tools — line 45
# variable: directory — line 46
# variable: environment — line 47
# variable: key — line 49
# variable: value — line 49
# variable: commit — line 77
# variable: module — line 90
# variable: binary — line 104
# variable: info — line 122
# variable: lab_sha — line 130
# variable: receipt — line 133
# END CODE MAP

from __future__ import annotations

import hashlib
import json
import os
import platform
import subprocess
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    """Verify exact source/toolchain/module sum, mechanically update a disposable upstream checkout, build and record provenance."""
    if platform.system() != "Linux":
        raise ValueError(
            "dedicated Linux build host required; no local toolchain changes"
        )
    spec = json.loads((ROOT / "tools.lock.json").read_text(encoding="utf-8"))[
        "openbao_build"
    ]
    version = subprocess.check_output(["go", "version"], text=True, timeout=10).split()
    if version[2] != spec["go_version"]:
        raise ValueError("exact patched Go toolchain required")
    tools = ROOT / ".tools"
    directory = tools / ("bao-source-" + uuid.uuid4().hex)
    environment = {
        key: value
        for key, value in os.environ.items()
        if key
        not in {"GOFLAGS", "GOTOOLCHAIN", "GOPROXY", "GOSUMDB", "GOWORK", "CGO_ENABLED"}
    }
    environment.update(
        GOTOOLCHAIN="local",
        GOPROXY="https://proxy.golang.org",
        GOSUMDB="sum.golang.org",
        GOWORK="off",
        CGO_ENABLED="0",
    )
    subprocess.run(
        [
            "git",
            "-c",
            "credential.helper=",
            "clone",
            "--depth",
            "1",
            "--branch",
            spec["tag"],
            "https://github.com/openbao/openbao.git",
            str(directory),
        ],
        env=environment,
        check=True,
        timeout=180,
    )
    commit = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=directory, text=True, timeout=10
    ).strip()
    if commit != spec["upstream_commit"]:
        raise ValueError("upstream tag/commit mismatch")
    # Standard Go tooling updates dependency metadata; no generated contribution is submitted upstream.
    subprocess.run(
        ["go", "get", "golang.org/x/net@" + spec["x_net"]],
        cwd=directory,
        env=environment,
        check=True,
        timeout=300,
    )
    module = json.loads(
        subprocess.check_output(
            ["go", "mod", "download", "-json", "golang.org/x/net@" + spec["x_net"]],
            cwd=directory,
            env=environment,
            text=True,
            timeout=60,
        )
    )
    if module["Version"] != spec["x_net"] or module["Sum"] != spec["x_net_sum"]:
        raise ValueError("reviewed module checksum mismatch")
    subprocess.run(
        ["go", "mod", "verify"], cwd=directory, env=environment, check=True, timeout=120
    )
    binary = tools / "bao"
    subprocess.run(
        [
            "go",
            "build",
            "-p",
            "2",
            "-trimpath",
            "-buildvcs=true",
            "-o",
            str(binary),
            ".",
        ],
        cwd=directory,
        env=environment,
        check=True,
        timeout=900,
    )
    info = subprocess.check_output(
        ["go", "version", "-m", str(binary)], text=True, timeout=10
    )
    if (
        spec["go_version"] not in info
        or "golang.org/x/net\t" + spec["x_net"] not in info
    ):
        raise ValueError("compiled dependency/toolchain identity mismatch")
    lab_sha = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True, timeout=10
    ).strip()
    receipt = {
        "source_sha": lab_sha,
        "upstream_sha": commit,
        "tag": spec["tag"],
        "go_version": spec["go_version"],
        "x_net": module["Version"],
        "x_net_sum": module["Sum"],
        "binary_sha256": hashlib.sha256(binary.read_bytes()).hexdigest(),
        "go_mod_sha256": hashlib.sha256(
            (directory / "go.mod").read_bytes()
        ).hexdigest(),
        "go_sum_sha256": hashlib.sha256(
            (directory / "go.sum").read_bytes()
        ).hexdigest(),
    }
    (tools / "bao-build.json").write_text(
        json.dumps(receipt, sort_keys=True) + "\n", encoding="utf-8", newline="\n"
    )
    print("PATCHED_OPENBAO_BUILD " + json.dumps(receipt), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
