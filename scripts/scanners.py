"""Install only hash-pinned official Linux scanner binaries. Created by Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# variable: ROOT — line 40
# variable: MAX_DOWNLOAD — line 41
# definition: install — line 44
# parameter: name — line 44
# variable: lock — line 46
# variable: repositories — line 49
# variable: prefix — line 55
# variable: output — line 60
# variable: digest — line 62
# variable: total — line 63
# variable: temporary — line 64
# variable: archive_path — line 65
# variable: response — line 67
# variable: stream — line 68
# variable: data — line 70
# variable: total — line 71
# variable: archive — line 78
# variable: member — line 79
# variable: source — line 82
# variable: target — line 85
# definition: main — line 92
# variable: parser — line 94
# variable: arguments — line 96
# END CODE MAP

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import tarfile
import tempfile
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAX_DOWNLOAD = 256 * 1024 * 1024


def install(name: str) -> Path:
    """Fetch a fixed official release, verify its pinned digest, and copy one regular binary."""
    lock = json.loads((ROOT / "tools.lock.json").read_text(encoding="utf-8"))["tools"][
        name
    ]
    repositories = {
        "gitleaks": "gitleaks/gitleaks",
        "trivy": "aquasecurity/trivy",
        "actionlint": "rhysd/actionlint",
        "bao": "openbao/openbao",
    }
    prefix = (
        f"https://github.com/{repositories[name]}/releases/download/v{lock['version']}/"
    )
    if not lock["url"].startswith(prefix):
        raise ValueError("tool source must be the pinned official repository")
    output = ROOT / ".tools"
    output.mkdir(exist_ok=True, mode=0o700)
    digest = hashlib.sha256()
    total = 0
    with tempfile.TemporaryDirectory(dir=output) as temporary:
        archive_path = Path(temporary) / "tool.tar.gz"
        with (
            urllib.request.urlopen(lock["url"], timeout=60) as response,
            archive_path.open("wb") as stream,
        ):
            while data := response.read(1024 * 1024):
                total += len(data)
                if total > MAX_DOWNLOAD:
                    raise ValueError("scanner download exceeds size cap")
                digest.update(data)
                stream.write(data)
        if digest.hexdigest() != lock["sha256"]:
            raise ValueError("scanner checksum mismatch; binary will not be executed")
        with tarfile.open(archive_path, "r:gz") as archive:
            member = archive.getmember(name)
            if not member.isfile() or member.size > MAX_DOWNLOAD:
                raise ValueError("scanner must be a bounded regular binary")
            source = archive.extractfile(member)
            if source is None:
                raise ValueError("scanner binary is missing")
            with source, (Path(temporary) / name).open("wb") as target:
                shutil.copyfileobj(source, target)
            os.chmod(Path(temporary) / name, 0o700)
            os.replace(Path(temporary) / name, output / name)
    return output / name


def main() -> int:
    """Install one allowlisted scanner; credentials and downloaded archive contents are not logged."""
    parser = argparse.ArgumentParser()
    parser.add_argument("name", choices=["gitleaks", "trivy", "actionlint", "bao"])
    arguments = parser.parse_args()
    print(install(arguments.name))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
