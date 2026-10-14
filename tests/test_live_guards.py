"""Cross-platform destructive-stage ownership, acknowledgment, deadline and TLS-copy contracts. Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# definition: test_host_refusal — line 47
# parameter: ack — line 47
# parameter: system — line 47
# variable: run — line 51
# definition: test_output_canonicalization — line 58
# parameter: tmp_path — line 58
# variable: bad — line 62
# definition: test_identity_guard — line 75
# variable: owner — line 77
# variable: name — line 78
# variable: metadata — line 79
# variable: bad — line 87
# variable: target — line 87
# definition: test_poll_and_port — line 97
# definition: test_private_tls_tar — line 105
# parameter: tmp_path — line 105
# variable: cert — line 107
# variable: key — line 107
# variable: raw — line 110
# variable: archive — line 111
# variable: member — line 115
# END CODE MAP

import io
import tarfile
from pathlib import Path
from unittest.mock import patch

import pytest

from scripts.live_drill import (
    LABEL,
    Docker,
    output_directory,
    owned,
    port,
    tls_archive,
    wait,
)


@pytest.mark.parametrize(
    "system,ack", [("Windows", True), ("Darwin", True), ("Linux", False)]
)
def test_host_refusal(system, ack):
    """No Docker subprocess can run on the local Windows PC or without disposable-host acknowledgement."""
    with (
        patch("scripts.live_drill.platform.system", return_value=system),
        patch("scripts.live_drill.subprocess.run") as run,
    ):
        with pytest.raises(ValueError):
            Docker(ack)
        run.assert_not_called()


def test_output_canonicalization(tmp_path: Path):
    """Traversal, deep/unsafe components and symlink observations fail before output creation."""
    with patch("scripts.live_drill.ROOT", tmp_path):
        assert output_directory(tmp_path / "out/demo") == tmp_path / "out/demo"
        for bad in [
            tmp_path / "out/../../escape",
            tmp_path / "out",
            tmp_path / 'out/quote"injection',
            tmp_path / "out/a/b/c/d",
        ]:
            with pytest.raises(ValueError):
                output_directory(bad)
        with patch.object(Path, "is_symlink", return_value=True):
            with pytest.raises(ValueError):
                output_directory(tmp_path / "out/demo")


def test_identity_guard():
    """Correct scoped ownership succeeds; wrong label, name or arbitrary resource target fails."""
    owner = "a" * 20
    name = "sr-" + owner + "-db"
    metadata = {"Name": "/" + name, "Config": {"Labels": {LABEL: owner}}}
    owned(metadata, name, owner)
    owned(
        {"Name": "sr-" + owner + "-net", "Labels": {LABEL: owner}},
        "sr-" + owner + "-net",
        owner,
        network=True,
    )
    for bad, target in [
        ({}, name),
        (metadata, "postgres"),
        (metadata | {"Name": "/other"}, name),
        ({"Name": name, "Config": {"Labels": {LABEL: "wrong"}}}, name),
    ]:
        with pytest.raises(ValueError):
            owned(bad, target, owner)


def test_poll_and_port():
    """A zero deadline fails, actual readiness succeeds and OS allocation yields a concrete port."""
    wait(lambda: True)
    with pytest.raises(RuntimeError, match="deadline"):
        wait(lambda: False, 0)
    assert 0 < port() < 65536


def test_private_tls_tar(tmp_path: Path):
    """Generated tar is precisely two regular files with non-root UID and private key mode, not arbitrary paths."""
    key, cert = tmp_path / "key", tmp_path / "cert"
    key.write_bytes(b"synthetic key fixture")
    cert.write_bytes(b"synthetic cert fixture")
    raw = tls_archive(key, cert, 70, 70)
    with tarfile.open(fileobj=io.BytesIO(raw)) as archive:
        assert archive.getnames() == ["server.key", "server.crt"]
        assert archive.getmember("server.key").mode == 0o600
        assert all(
            member.uid == 70 and member.isfile() for member in archive.getmembers()
        )
