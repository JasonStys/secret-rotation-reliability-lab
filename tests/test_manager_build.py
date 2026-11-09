"""Independent rejection oracles for maintained manager module/checksum identity. Created by Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# variable: SPEC — line 25
# definition: build_info — line 30
# variable: item — line 38
# variable: name — line 38
# definition: test_exact_compiled_graph_and_no_v3 — line 43
# variable: info — line 45
# variable: changed — line 47
# definition: test_both_module_archive_and_metadata_checksum_required — line 58
# variable: expected — line 60
# variable: actual — line 61
# variable: field — line 67
# variable: changed — line 68
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
