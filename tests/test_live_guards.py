"""Cross-platform destructive-stage ownership, acknowledgment, deadline and TLS-copy contracts. Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# definition: test_host_refusal — line 61
# parameter: ack — line 61
# parameter: system — line 61
# variable: run — line 65
# definition: test_output_canonicalization — line 72
# parameter: tmp_path — line 72
# variable: bad — line 76
# definition: test_declarative_audit_config — line 89
# variable: text — line 91
# definition: test_fixture_trace_privacy — line 101
# parameter: capsys — line 101
# variable: client — line 107
# variable: text — line 117
# definition: test_internal_database_address — line 125
# variable: metadata — line 127
# variable: network — line 131
# variable: address — line 133
# variable: altered — line 134
# definition: test_identity_guard — line 152
# variable: owner — line 154
# variable: name — line 155
# variable: metadata — line 156
# variable: bad — line 164
# variable: target — line 164
# definition: test_poll_and_port — line 174
# definition: test_private_tls_tar — line 182
# parameter: tmp_path — line 182
# variable: cert — line 184
# variable: key — line 184
# variable: raw — line 187
# variable: archive — line 188
# variable: member — line 192
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
    database_address,
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


def test_internal_database_address():
    """Reject unrelated/public/multiple/published endpoints; only the checked internal subnet address is usable."""
    metadata = {
        "NetworkSettings": {"Networks": {"owned-net": {"IPAddress": "172.19.0.2"}}},
        "HostConfig": {"PortBindings": {}},
    }
    network = {"Internal": True, "IPAM": {"Config": [{"Subnet": "172.19.0.0/16"}]}}
    assert database_address(metadata, network, "owned-net") == "172.19.0.2"
    for address in ["8.8.8.8", "127.0.0.1", "172.20.0.2", "::1"]:
        altered = {
            "NetworkSettings": {"Networks": {"owned-net": {"IPAddress": address}}},
            "HostConfig": {"PortBindings": {}},
        }
        with pytest.raises(ValueError):
            database_address(altered, network, "owned-net")
    with pytest.raises(ValueError):
        database_address(metadata, network | {"Internal": False}, "owned-net")
    with pytest.raises(ValueError):
        database_address(
            metadata | {"HostConfig": {"PortBindings": {"5432/tcp": [{}]}}},
            network,
            "owned-net",
        )
    with pytest.raises(ValueError):
        database_address(metadata, network, "wrong-net")


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
