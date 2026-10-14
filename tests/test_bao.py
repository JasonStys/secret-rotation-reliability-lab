"""Provider protocol and transport adversarial tests; fake sockets never access outside networks. Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# definition: transport — line 55
# definition: test_endpoint — line 77
# parameter: url — line 77
# definition: test_response_boundaries — line 114
# parameter: category — line 114
# parameter: raw — line 114
# parameter: retry — line 114
# parameter: status — line 114
# variable: client — line 116
# variable: connection — line 117
# variable: response — line 118
# attribute: return_value — line 119
# attribute: status — line 119
# variable: result — line 121
# definition: test_transport_errors — line 135
# parameter: category — line 135
# parameter: failure — line 135
# variable: client — line 137
# variable: connection — line 138
# attribute: side_effect — line 139
# variable: result — line 141
# definition: test_success_requests_and_limits — line 147
# variable: client — line 149
# variable: connection — line 150
# variable: response — line 151
# attribute: return_value — line 152
# attribute: status — line 152
# variable: factory — line 155
# attribute: return_value — line 160
# attribute: status — line 160
# variable: method — line 166
# variable: path — line 166
# definition: reply — line 178
# definition: test_provider_success_and_malformed — line 188
# variable: mock — line 190
# attribute: return_value — line 191
# variable: provider — line 192
# variable: result — line 193
# variable: bad — line 196
# attribute: return_value — line 204
# END CODE MAP

import json
import ssl
from unittest.mock import MagicMock, patch

import pytest

from rotation.bao import MAX_BODY, BaoProvider, Transport
from rotation.contracts import ProviderError


def transport():
    """Construct a verifying transport with a mocked standard CA loader, not a disabled TLS switch."""
    with patch(
        "rotation.bao.ssl.create_default_context",
        return_value=ssl.create_default_context(),
    ):
        return Transport("https://127.0.0.1:8200", "fictional-ca", "fictional-token")


@pytest.mark.parametrize(
    "url",
    [
        "http://127.0.0.1:8200",
        "https://localhost:8200",
        "https://8.8.8.8:8200",
        "https://user@127.0.0.1:8200",
        "https://127.0.0.1",
        "https://127.0.0.1:8200/a",
        "https://127.0.0.1:8200?q=1",
        "https://127.0.0.1:8200#x",
    ],
)
def test_endpoint(url):
    """Plain HTTP, DNS/nonloopback, credentials, query and path redirects cannot transmit a token."""
    with pytest.raises(ValueError):
        Transport(url, "unused")


@pytest.mark.parametrize(
    "status,raw,category,retry",
    [
        (403, b"secret", "denied", False),
        (401, b"secret", "denied", False),
        (503, b"secret", "unavailable", True),
        (429, b"secret", "unavailable", True),
        (307, b"redirect", "invalid", False),
        (400, b"secret", "invalid", False),
        (200, b"[]", "invalid", False),
        (200, b'{"a":1,"a":2}', "invalid", False),
        (200, b'{"a":NaN}', "invalid", False),
        (200, b"not-json", "invalid", False),
        (200, b"\xff", "invalid", False),
        (200, b"x" * (MAX_BODY + 1), "invalid", False),
    ],
    ids=[
        "forbidden",
        "unauthorized",
        "unavailable",
        "rate-limit",
        "redirect",
        "bad-request",
        "array",
        "duplicate",
        "nan",
        "malformed",
        "invalid-utf8",
        "oversize",
    ],
)
def test_response_boundaries(status, raw, category, retry):
    """Transport refuses malformed/redirect/oversize payloads and never echoes provider response bodies."""
    client = transport()
    connection = MagicMock()
    response = connection.getresponse.return_value
    response.status, response.read.return_value = status, raw
    with patch("rotation.bao.http.client.HTTPSConnection", return_value=connection):
        with pytest.raises(ProviderError) as result:
            client.request("GET", "database/creds/reader")
    assert result.value.category == category and result.value.retryable is retry
    assert "secret" not in str(result.value)
    connection.close.assert_called_once()


@pytest.mark.parametrize(
    "failure,category",
    [
        (TimeoutError("private password"), "unavailable"),
        (ssl.SSLError("private token"), "tls"),
    ],
)
def test_transport_errors(failure, category):
    """Raw TLS/socket exception text is discarded, not put into a public report or exception string."""
    client = transport()
    connection = MagicMock()
    connection.request.side_effect = failure
    with patch("rotation.bao.http.client.HTTPSConnection", return_value=connection):
        with pytest.raises(ProviderError) as result:
            client.request("GET", "sys/init")
    assert result.value.category == category and "private" not in str(result.value)
    assert result.value.__suppress_context__


def test_success_requests_and_limits():
    """Success preserves certificate checks, fixed paths and two-second timeout; writes are byte-bounded."""
    client = transport()
    connection = MagicMock()
    response = connection.getresponse.return_value
    response.status, response.read.return_value = 200, b'{"initialized":false}'
    with patch(
        "rotation.bao.http.client.HTTPSConnection", return_value=connection
    ) as factory:
        assert client.request("GET", "sys/init") == {"initialized": False}
        factory.assert_called_once_with(
            "127.0.0.1", 8200, context=client._context, timeout=2
        )
        response.status, response.read.return_value = 204, b""
        assert client.request("POST", "sys/unseal", {"key": "fictional"}) == {}
    assert (
        client._context.check_hostname
        and client._context.verify_mode == ssl.CERT_REQUIRED
    )
    for method, path in [
        ("DELETE", "sys/init"),
        ("GET", "../secret"),
        ("GET", "sys//init"),
        ("GET", "sys/init?x"),
    ]:
        with pytest.raises(ValueError):
            client.request(method, path)
    with pytest.raises(ValueError, match="cap"):
        client.request("POST", "sys/init", {"x": "a" * MAX_BODY})


def reply():
    """Return an independent synthetic OpenBao HTTP response with real API field shapes."""
    return {
        "lease_id": "database/creds/reader/fictional",
        "lease_duration": 12,
        "renewable": True,
        "data": {"username": "fictional-user", "password": "fictional-password"},
    }


def test_provider_success_and_malformed():
    """Start time precedes issuance; each required field must validate, including exact int/bool TTL semantics."""
    mock = MagicMock()
    mock.request.return_value = reply()
    provider = BaoProvider(mock, clock=lambda: 100)
    result = provider.issue()
    assert result.started_at == 100 and result.ttl == 12
    mock.request.assert_called_once_with("GET", "database/creds/reader")
    for bad in [
        {},
        reply() | {"data": []},
        reply() | {"lease_duration": True},
        reply() | {"renewable": 1},
        reply() | {"lease_id": "../escape"},
        reply() | {"data": {"username": "x"}},
    ]:
        mock.request.return_value = bad
        with pytest.raises(ProviderError, match="invalid"):
            provider.issue()
    assert len(json.dumps(reply())) < MAX_BODY
