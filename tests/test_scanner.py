"""Scanner regression: actual post-build rootfs mode and nonempty Go inventory required. Created by Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# definition: test_go_scan_mode_and_inventory — line 40
# parameter: accepted — line 40
# parameter: results — line 40
# parameter: tmp_path — line 40
# variable: tools — line 42
# definition: scan — line 46
# parameter: args — line 46
# parameter: kwargs — line 46
# END CODE MAP

import json
from pathlib import Path
from unittest.mock import patch

import pytest

from scripts import bao_check


@pytest.mark.parametrize(
    "results,accepted",
    [
        ([], False),
        ([{"Type": "gobinary", "Packages": []}], False),
        (
            [
                {
                    "Type": "gobinary",
                    "Packages": [{"Name": "fictional"}],
                    "Vulnerabilities": [{}],
                }
            ],
            False,
        ),
        ([{"Type": "gobinary", "Packages": [{"Name": "fictional"}]}], True),
    ],
)
def test_go_scan_mode_and_inventory(tmp_path: Path, results, accepted):
    """A scanner's zero exit cannot bypass absent inventory/advisories; fixed args preserve the gate."""
    tools = tmp_path / ".tools"
    tools.mkdir()
    (tools / "bao").write_bytes(b"fictional executable fixture, never executed")

    def scan(args, **kwargs):
        """Mock external scanner I/O; assert mode/severity/no exclusions and emit controlled JSON."""
        assert (
            args[1] == "rootfs"
            and args[args.index("--severity") + 1] == "HIGH,CRITICAL"
        )
        assert kwargs["check"] is True and kwargs["timeout"] == 180
        Path(args[args.index("--output") + 1]).write_text(
            json.dumps({"Results": results}), encoding="utf-8"
        )

    with (
        patch.object(bao_check, "ROOT", tmp_path),
        patch.object(bao_check.subprocess, "run", side_effect=scan),
    ):
        if accepted:
            assert bao_check.main() == 0
        else:
            with pytest.raises(ValueError):
                bao_check.main()
