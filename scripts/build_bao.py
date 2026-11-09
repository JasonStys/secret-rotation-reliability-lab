"""Build pinned upstream OpenBao with reviewed maintained authentication/network dependencies, never suppressing advisories. Created by Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# variable: ROOT — line 49
# definition: verify_module — line 52
# parameter: expected — line 52
# parameter: module — line 52
# definition: verify_build_info — line 62
# parameter: info — line 62
# parameter: spec — line 62
# variable: line — line 64
# variable: lines — line 64
# variable: dependencies — line 65
# variable: line — line 66
# variable: name — line 70
# variable: item — line 73
# variable: name — line 73
# variable: line — line 75
# definition: main — line 80
# variable: spec — line 86
# variable: version — line 89
# variable: tools — line 92
# variable: directory — line 93
# variable: environment — line 94
# variable: key — line 96
# variable: value — line 96
# variable: commit — line 124
# variable: modules — line 130
# variable: item — line 135
# variable: name — line 135
# variable: item — line 145
# variable: name — line 145
# variable: module — line 146
# variable: binary — line 177
# variable: info — line 195
# variable: lab_sha — line 199
# variable: receipt — line 202
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


def verify_module(module: dict, expected: dict) -> None:
    """Reject changed archive AND go.mod identities, even when version text matches."""
    if (
        module.get("Version") != expected["version"]
        or module.get("Sum") != expected["sum"]
        or module.get("GoModSum") != expected["go_mod_sum"]
    ):
        raise ValueError("reviewed module checksum mismatch")


def verify_build_info(info: str, spec: dict) -> None:
    """Require exact linked module identities and reject any remaining vulnerable jose/v3 dependency."""
    lines = [line.split() for line in info.splitlines()]
    dependencies = {
        line[1]: line[2:] for line in lines if len(line) >= 4 and line[0] == "dep"
    }
    if (
        spec["go_version"] not in info.splitlines()[0]
        or any(name == "github.com/go-jose/go-jose/v3" for name in dependencies)
        or any(
            dependencies.get(name) != [item["version"], item["sum"]]
            for name, item in spec["modules"].items()
        )
        or any(line and line[0] == "=>" for line in lines)
    ):
        raise ValueError("compiled dependency/toolchain identity mismatch")


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
    # CAP's maintained v0.15 migration removes unpatched jose/v3; do not fork crypto or ignore it.
    modules = spec["modules"]
    subprocess.run(
        [
            "go",
            "get",
            *[name + "@" + item["version"] for name, item in modules.items()],
        ],
        cwd=directory,
        env=environment,
        check=True,
        timeout=300,
    )
    subprocess.run(
        ["go", "mod", "tidy"], cwd=directory, env=environment, check=True, timeout=300
    )
    for name, item in modules.items():
        module = json.loads(
            subprocess.check_output(
                ["go", "mod", "download", "-json", name + "@" + item["version"]],
                cwd=directory,
                env=environment,
                text=True,
                timeout=60,
            )
        )
        verify_module(module, item)
    subprocess.run(
        ["go", "mod", "verify"], cwd=directory, env=environment, check=True, timeout=120
    )
    # Actual upstream integration tests exercise authentication callers of the migrated CAP API.
    subprocess.run(
        [
            "go",
            "test",
            "-p",
            "2",
            "-short",
            "-timeout",
            "5m",
            "./internal/builtin/credential/jwt",
            "./internal/builtin/credential/kubernetes",
        ],
        cwd=directory,
        env=environment,
        check=True,
        timeout=660,
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
    verify_build_info(info, spec)
    lab_sha = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True, timeout=10
    ).strip()
    receipt = {
        "source_sha": lab_sha,
        "upstream_sha": commit,
        "tag": spec["tag"],
        "go_version": spec["go_version"],
        "modules": modules,
        "upstream_auth_tests": "PASS jwt+kubernetes -short",
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
