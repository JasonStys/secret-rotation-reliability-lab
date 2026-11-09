"""Build pinned upstream OpenBao with reviewed maintained authentication/network dependencies, never suppressing advisories. Created by Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# variable: ROOT — line 66
# definition: verify_module — line 69
# parameter: expected — line 69
# parameter: module — line 69
# definition: build_identity — line 79
# parameter: info — line 79
# parameter: spec — line 79
# variable: line — line 81
# variable: lines — line 81
# variable: dependencies — line 82
# variable: line — line 83
# variable: version — line 85
# variable: failures — line 90
# variable: item — line 95
# variable: name — line 95
# variable: previous — line 98
# variable: reviewed_replacements — line 99
# variable: line — line 100
# variable: previous — line 102
# variable: expected — line 104
# variable: previous — line 109
# variable: value — line 117
# variable: name — line 119
# definition: verify_build_info — line 127
# parameter: info — line 127
# parameter: spec — line 127
# variable: identity — line 129
# definition: main — line 135
# variable: spec — line 141
# variable: version — line 144
# variable: tools — line 147
# variable: directory — line 148
# variable: environment — line 149
# variable: key — line 151
# variable: value — line 151
# variable: commit — line 179
# variable: modules — line 185
# variable: item — line 190
# variable: name — line 190
# variable: item — line 200
# variable: name — line 200
# variable: module — line 201
# variable: binary — line 232
# variable: info — line 250
# variable: identity — line 253
# variable: why — line 255
# variable: public — line 265
# variable: line — line 267
# variable: lab_sha — line 272
# variable: receipt — line 275
# END CODE MAP

from __future__ import annotations

import hashlib
import json
import os
import platform
import re
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


def build_identity(info: str, spec: dict) -> dict:
    """Expose only reviewed public module identities and failed invariant names; never full build/environment output."""
    lines = [line.split() for line in info.splitlines()]
    dependencies = {
        line[1]: line[2:] for line in lines if len(line) >= 3 and line[0] == "dep"
    }
    version = (
        info.splitlines()[0].rsplit(": ", 1)[-1].split()[0]
        if info.splitlines() and info.splitlines()[0].split()
        else "missing"
    )
    failures = []
    if version != spec["go_version"]:
        failures.append("toolchain")
    if "github.com/go-jose/go-jose/v3" in dependencies:
        failures.append("jose_v3_linked")
    for name, item in spec["modules"].items():
        if dependencies.get(name) != [item["version"], item["sum"]]:
            failures.append("module:" + name)
    previous = None
    reviewed_replacements = []
    for line in lines:
        if line and line[0] == "dep":
            previous = line[1] if len(line) >= 3 else None
        elif line and line[0] == "=>":
            expected = spec["local_replacements"].get(previous)
            if expected is None or line[1:] != [expected, "(devel)"]:
                failures.append("unexpected_replacement")
            else:
                reviewed_replacements.append(previous)
            previous = None
    return {
        "toolchain": version if re.fullmatch(r"go[0-9.]+", version) else "unrecognized",
        "reviewed_modules": {
            name: [
                value
                if re.fullmatch(r"[A-Za-z0-9+/:=._-]{1,150}", value)
                else "unrecognized"
                for value in dependencies.get(name, [])[:2]
            ]
            for name in spec["modules"]
        },
        "jose_v3_linked": "github.com/go-jose/go-jose/v3" in dependencies,
        "reviewed_in_tree_replacements": sorted(reviewed_replacements),
        "failed_invariants": failures[:20],
    }


def verify_build_info(info: str, spec: dict) -> None:
    """Require exact linked identities; allow only six exact upstream source-bound in-tree replacements."""
    identity = build_identity(info, spec)
    print("COMPILED_IDENTITY " + json.dumps(identity, sort_keys=True), flush=True)
    if identity["failed_invariants"]:
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
    identity = build_identity(info, spec)
    if identity["jose_v3_linked"]:
        why = subprocess.run(
            ["go", "mod", "why", "-m", "github.com/go-jose/go-jose/v3"],
            cwd=directory,
            env=environment,
            text=True,
            capture_output=True,
            timeout=60,
            check=False,
        )
        # Go's known public dependency path output only; no environment or arbitrary stderr is logged.
        public = [
            line[:200]
            for line in why.stdout.splitlines()[:40]
            if re.fullmatch(r"[#A-Za-z0-9/._() -]{1,200}", line)
        ]
        print("JOSE_V3_IMPORT_PATH " + "\n".join(public), flush=True)
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
        "compiled_identity": identity,
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
