"""Strict evidence schema, output privacy, real CLI control flow and aggregate negative tests. Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# definition: report — line 39
# definition: test_simulation_and_render — line 44
# variable: value — line 46
# variable: case — line 47
# variable: text — line 48
# definition: test_report_top_level — line 68
# parameter: change — line 68
# definition: test_report_case_and_counter_negatives — line 74
# variable: change — line 76
# variable: value — line 83
# variable: value — line 87
# variable: value — line 91
# variable: value — line 95
# definition: test_files_and_cli — line 103
# parameter: capsys — line 103
# parameter: tmp_path — line 103
# variable: destination — line 105
# variable: failed — line 114
# variable: invalid — line 128
# definition: test_symlink_guard_without_system_privileges — line 140
# parameter: tmp_path — line 140
# END CODE MAP

import copy
import json
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

from rotation.__main__ import main
from rotation.evidence import read_report, render, validate, write_report
from rotation.simulation import simulate


def report():
    """Exercise the eight real offline assertions; clearly label their aggregate as simulation."""
    return simulate("a" * 40)


def test_simulation_and_render():
    """Public HTML is inert and aggregate counters contain no fictional password/username."""
    value = report()
    assert all(case["passed"] for case in value["cases"])
    text = render(value)
    assert "simulation evidence" in text and "Jason Stys" in text
    assert "<script" not in text and "not-a-real" not in json.dumps(value)
    assert value["metrics"]["fallbacks"] == 1


@pytest.mark.parametrize(
    "change",
    [
        {"token": "private"},
        {"schema": True},
        {"mode": []},
        {"mode": "unknown"},
        {"source_sha": "bad"},
        {"cases": []},
        {"cases": "bad"},
        {"metrics": {}},
        {"metrics": "bad"},
    ],
)
def test_report_top_level(change):
    """Unknown secret fields and malformed identity/aggregate types are rejected without publication."""
    with pytest.raises(ValueError):
        validate(report() | change)


def test_report_case_and_counter_negatives():
    """Cases must be unique, exact, bool, finite, bounded; counter labels cannot hide private content."""
    for change in [
        {"password": "private"},
        {"name": "<script>"},
        {"passed": 1},
        {"duration_ms": float("nan")},
        {"duration_ms": -1},
    ]:
        value = report()
        value["cases"][0].update(change)
        with pytest.raises(ValueError):
            validate(value)
    value = report()
    value["cases"][1] = copy.deepcopy(value["cases"][0])
    with pytest.raises(ValueError):
        validate(value)
    value = report()
    value["cases"][0] = "bad"
    with pytest.raises(ValueError):
        validate(value)
    value = report()
    value["metrics"]["requests"] = True
    with pytest.raises(ValueError):
        validate(value)
    with pytest.raises(ValueError):
        validate([])


def test_files_and_cli(tmp_path: Path, capsys):
    """Real file/CLI paths succeed, fail on failed cases/malformed data and refuse report overwrite."""
    destination = tmp_path / "report"
    write_report(report(), destination)
    assert read_report(destination / "report.json")["mode"] == "simulation"
    with pytest.raises(FileExistsError):
        write_report(report(), destination)
    with patch.object(
        sys, "argv", ["rotation", "report", str(destination / "report.json")]
    ):
        assert main() == 0
    failed = report()
    failed["cases"][0]["passed"] = False
    write_report(failed, tmp_path / "failed")
    with patch.object(
        sys, "argv", ["rotation", "report", str(tmp_path / "failed/report.json")]
    ):
        assert main() == 1
    with (
        patch.object(
            sys, "argv", ["rotation", "demo", "--output", str(tmp_path / "demo")]
        ),
        patch("rotation.__main__.subprocess.check_output", return_value="b" * 40),
    ):
        assert main() == 0
    invalid = tmp_path / "invalid.json"
    invalid.write_text('{"password":"private"}', encoding="utf-8")
    with patch.object(sys, "argv", ["rotation", "report", str(invalid)]):
        assert main() == 2
    assert "private" not in capsys.readouterr().out
    invalid.write_bytes(b"x" * 65537)
    with pytest.raises(ValueError):
        read_report(invalid)
    with pytest.raises(ValueError):
        read_report(tmp_path / "absent")


def test_symlink_guard_without_system_privileges(tmp_path: Path):
    """Mock actual Path symlink observations to exercise refusal portably without developer-mode privileges."""
    with patch.object(Path, "is_symlink", return_value=True):
        with pytest.raises(ValueError):
            write_report(report(), tmp_path / "report")
        with pytest.raises(ValueError):
            read_report(tmp_path / "report.json")
