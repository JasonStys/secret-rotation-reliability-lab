"""Independent rejection oracles for maintained manager module/checksum identity. Created by Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# variable: SPEC — line 34
# definition: build_info — line 39
# variable: item — line 47
# variable: name — line 47
# definition: test_exact_compiled_graph_and_no_v3 — line 52
# variable: info — line 54
# variable: changed — line 56
# definition: test_both_module_archive_and_metadata_checksum_required — line 67
# variable: expected — line 69
# variable: actual — line 70
# variable: field — line 76
# variable: changed — line 77
# definition: test_only_exact_upstream_in_tree_replacements — line 83
# parameter: capsys — line 83
# variable: info — line 85
# variable: name — line 86
# variable: path — line 86
# variable: info — line 87
# variable: content — line 90
# definition: test_safe_diagnostics_and_empty_metadata — line 99
# variable: result — line 104
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
