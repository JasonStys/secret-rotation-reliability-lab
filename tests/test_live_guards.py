"""Cross-platform destructive-stage ownership, acknowledgment, deadline and TLS-copy contracts. Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# definition: test_host_refusal — line 55
# parameter: ack — line 55
# parameter: system — line 55
# variable: run — line 59
# definition: test_output_canonicalization — line 66
# parameter: tmp_path — line 66
# variable: bad — line 70
# definition: test_declarative_audit_config — line 83
# variable: text — line 85
# definition: test_fixture_trace_privacy — line 95
# parameter: capsys — line 95
# variable: client — line 101
# variable: text — line 111
# definition: test_identity_guard — line 119
# variable: owner — line 121
# variable: name — line 122
# variable: metadata — line 123
# variable: bad — line 131
# variable: target — line 131
# definition: test_poll_and_port — line 141
# definition: test_private_tls_tar — line 149
# parameter: tmp_path — line 149
# variable: cert — line 151
# variable: key — line 151
# variable: raw — line 154
# variable: archive — line 155
# variable: member — line 159
# END CODE MAP

import io
import tarfile
from pathlib import Path
from unittest.mock import patch

import pytest

from scripts.live_drill import (
    LABEL,
    Docker,
    FixtureTransport,
    configuration,
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


def test_declarative_audit_config():
    """Use immutable declarative audit with escaped paths and raw logging false; unsafe API flag must remain absent."""
    text = configuration(
        "https://127.0.0.1:8200",
        Path('a"b.crt'),
        Path("private.key"),
        Path("audit.jsonl"),
    )
    assert 'audit "file" "file"' in text and 'log_raw = "false"' in text
    assert 'a\\"b.crt' in text and "unsafe_allow_api_audit_creation" not in text


def test_fixture_trace_privacy(capsys):
    """Unknown paths are rejected; a known failed operation logs only fixed names/categories, never body secrets."""
    from rotation.bao import Transport
    from rotation.contracts import ProviderError

    with patch("rotation.bao.ssl.create_default_context"):
        client = FixtureTransport(
            "https://127.0.0.1:8200", Path("unused"), "fictional-token"
        )
    with pytest.raises(ValueError):
        client.request("GET", "private-unknown")
    with patch.object(Transport, "request", side_effect=ProviderError("denied")):
        with pytest.raises(ProviderError):
            client.request(
                "POST", "sys/audit/unapproved", {"private": "never-log-this-body"}
            )
    text = capsys.readouterr().out
    assert (
        "denied" in text
        and "never-log-this-body" not in text
        and "fictional-token" not in text
    )


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
