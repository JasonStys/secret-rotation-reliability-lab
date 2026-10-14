"""Gate immutable pins, workflow permission/storage and credential tracking invariants. Created by Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# variable: ROOT — line 22
# definition: main — line 25
# variable: lock — line 27
# variable: value — line 34
# variable: path — line 39
# variable: text — line 40
# variable: term — line 43
# variable: action — line 52
# variable: tracked — line 57
# variable: path — line 65
# END CODE MAP

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    """Inspect source statically; fail on floating actions/images, artifact caches or tracked private outputs."""
    lock = json.loads((ROOT / "tools.lock.json").read_text(encoding="utf-8"))
    if not re.fullmatch(
        r"postgres:18-alpine@sha256:[a-f0-9]{64}", lock["postgres_image"]
    ) or "FROM " + lock["postgres_image"] not in (ROOT / "Dockerfile").read_text(
        encoding="utf-8"
    ):
        raise ValueError("immutable base required")
    for value in lock["tools"].values():
        if not re.fullmatch(r"[a-f0-9]{64}", value["sha256"]) or not value[
            "url"
        ].startswith("https://github.com/"):
            raise ValueError("official tool hash/source required")
    for path in (ROOT / ".github/workflows").glob("*.yml"):
        text = path.read_text(encoding="utf-8")
        if any(
            term in text
            for term in [
                "pull_request_target",
                "upload-artifact",
                "actions/cache",
                "write-all",
                "persist-credentials: true",
            ]
        ):
            raise ValueError("unsafe workflow permission/event/storage")
        for action in re.findall(r"uses: ([^\s]+)", text):
            if not re.fullmatch(
                r"[A-Za-z0-9_.-]+/[A-Za-z0-9_./-]+@[a-f0-9]{40}", action
            ):
                raise ValueError("full action commit required")
    tracked = (
        subprocess.check_output(["git", "ls-files", "-z"], cwd=ROOT)
        .decode()
        .split("\0")
    )
    if any(
        path.startswith(("out/", ".tools/", ".venv/"))
        or path.endswith((".key", ".pem", ".env", ".token", ".password"))
        for path in tracked
    ):
        raise ValueError("private/runtime files must not be tracked")
    print(
        "Pinned supply-chain, workflow storage and credential tracking contracts passed"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
