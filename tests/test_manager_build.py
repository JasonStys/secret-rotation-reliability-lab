"""Independent rejection oracles for maintained manager module/checksum identity. Created by Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# variable: SPEC — line 39
# definition: build_info — line 44
# variable: item — line 52
# variable: name — line 52
# definition: test_exact_compiled_graph_and_no_v3 — line 57
# variable: info — line 59
# variable: changed — line 61
# definition: test_both_module_archive_and_metadata_checksum_required — line 72
# variable: expected — line 74
# variable: actual — line 75
# variable: field — line 81
# variable: changed — line 82
# definition: test_only_exact_upstream_in_tree_replacements — line 88
# parameter: capsys — line 88
# variable: info — line 90
# variable: name — line 91
# variable: path — line 91
# variable: info — line 92
# variable: content — line 95
# definition: test_safe_diagnostics_and_empty_metadata — line 104
# variable: result — line 109
# definition: test_reviewed_fail_closed_patch_identity — line 116
# variable: patch — line 120
# variable: content — line 121
# variable: added — line 123
# variable: line — line 125
# END CODE MAP

import copy
import json
from pathlib import Path

import pytest

from scripts.build_bao import verify_build_info, verify_module

SPEC = json.loads(
    (Path(__file__).resolve().parents[1] / "tools.lock.json").read_text()
)["openbao_build"]


def build_info():
    """Construct standard go version -m text from the reviewed lock, never execute a fixture binary."""
    return (
        ".tools/bao: "
        + SPEC["go_version"]
        + "\n"
        + "".join(
            "\tdep\t" + name + "\t" + item["version"] + "\t" + item["sum"] + "\n"
            for name, item in SPEC["modules"].items()
        )
    )


def test_exact_compiled_graph_and_no_v3():
    """Accept all exact maintained dependencies; reject stale versions, omitted sums, v3 or replacement graphs."""
    info = build_info()
    verify_build_info(info, SPEC)
    for changed in (
        info.replace("v4.1.8", "v4.1.4"),
        info.replace("go1.27.3", "go1.27.2"),
        info.replace(SPEC["modules"]["golang.org/x/net"]["sum"], ""),
        info + "\tdep\tgithub.com/go-jose/go-jose/v3\tv3.0.5\th1:old\n",
        info + "\t=>\tlocal/fork\t(devel)\n",
    ):
        with pytest.raises(ValueError, match="identity mismatch"):
            verify_build_info(changed, SPEC)


def test_both_module_archive_and_metadata_checksum_required():
    """Archive/metadata tampering and equal-version substitution independently reject before building."""
    expected = SPEC["modules"]["github.com/hashicorp/cap"]
    actual = {
        "Version": expected["version"],
        "Sum": expected["sum"],
        "GoModSum": expected["go_mod_sum"],
    }
    verify_module(actual, expected)
    for field in actual:
        changed = copy.deepcopy(actual)
        changed[field] += "changed"
        with pytest.raises(ValueError, match="checksum mismatch"):
            verify_module(changed, expected)


def test_only_exact_upstream_in_tree_replacements(capsys):
    """Vendor-owned local modules are source-SHA-bound; changed paths or crypto forks remain rejected."""
    info = build_info()
    for name, path in SPEC["local_replacements"].items():
        info += "\tdep\t" + name + "\tv0.0.0\n\t=>\t" + path + "\t(devel)\n\n"
    verify_build_info(info, SPEC)
    assert "reviewed_in_tree_replacements" in capsys.readouterr().out
    for content in (
        info.replace("./sdk", "../outside"),
        info.replace("./api\t", "./api-changed\t"),
        info + "\tdep\tgithub.com/hashicorp/cap\tv0.15.0\n\t=>\t./sdk\t(devel)\n",
    ):
        with pytest.raises(ValueError):
            verify_build_info(content, SPEC)


def test_safe_diagnostics_and_empty_metadata():
    """Only fixed public fields are logged; missing/malformed toolchain and replacement identities fail closed."""
    from scripts.build_bao import build_identity

    assert build_identity("", SPEC)["failed_invariants"]
    result = build_identity(
        build_info().replace("go1.27.3", "private-token-with-controls\x00"), SPEC
    )
    assert result["toolchain"] == "unrecognized"
    assert "private-token" not in json.dumps(result)


def test_reviewed_fail_closed_patch_identity():
    """The precise lab patch is locked and only added Okta behavior is explicit rejection plus an actual Go test."""
    import hashlib

    patch = SPEC["source_patches"][0]
    content = (Path(__file__).resolve().parents[1] / patch["path"]).read_bytes()
    assert hashlib.sha256(content).hexdigest() == patch["sha256"]
    added = "\n".join(
        line[1:]
        for line in content.decode().splitlines()
        if line.startswith("+") and not line.startswith("+++")
    )
    assert (
        'return errors.New("Okta login MFA is unavailable in this lab build")' in added
    )
    assert "return nil" not in added and "TestLabOktaMFAUnavailable" in added
    assert "var core *Core" in added and "context.WithCancel" in added
    assert '-\t"github.com/okta/okta-sdk-golang/v2/okta"' in content.decode()
    assert hashlib.sha256(content + b"tamper").hexdigest() != patch["sha256"]
