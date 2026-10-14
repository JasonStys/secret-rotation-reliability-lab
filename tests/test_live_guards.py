"""Cross-platform destructive-stage ownership, acknowledgment, deadline and TLS-copy contracts. Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# definition: test_host_refusal — line 36
# parameter: ack — line 36
# parameter: system — line 36
# variable: run — line 40
# definition: test_identity_guard — line 47
# variable: owner — line 49
# variable: name — line 50
# variable: metadata — line 51
# variable: bad — line 59
# variable: target — line 59
# definition: test_poll_and_port — line 69
# definition: test_private_tls_tar — line 77
# parameter: tmp_path — line 77
# variable: cert — line 79
# variable: key — line 79
# variable: raw — line 82
# variable: archive — line 83
# variable: member — line 87
# END CODE MAP

import io
import tarfile
from pathlib import Path
from unittest.mock import patch

import pytest

from scripts.live_drill import LABEL, Docker, owned, port, tls_archive, wait


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
