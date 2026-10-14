"""Verified TLS, no redirects/proxies, bounded OpenBao JSON and safe provider errors. Created by Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# variable: MAX_BODY — line 61
# definition: unique — line 64
# parameter: pairs — line 64
# variable: result — line 66
# variable: key — line 67
# variable: value — line 67
# definition: invalid_constant — line 74
# parameter: value — line 74
# definition: Transport — line 79
# definition: __init__ — line 82
# parameter: ca — line 82
# parameter: endpoint — line 82
# parameter: self — line 82
# parameter: token — line 82
# variable: parsed — line 84
# attribute: port — line 98
# attribute: _token — line 99
# attribute: _context — line 100
# attribute: minimum_version — line 101
# definition: request — line 103
# parameter: body — line 104
# parameter: method — line 104
# parameter: path — line 104
# parameter: self — line 104
# variable: payload — line 113
# variable: connection — line 118
# variable: response — line 131
# variable: raw — line 138
# variable: result — line 143
# definition: BaoProvider — line 159
# definition: __init__ — line 162
# parameter: clock — line 163
# parameter: self — line 163
# parameter: transport — line 163
# attribute: transport — line 166
# attribute: clock — line 167
# definition: issue — line 169
# parameter: self — line 169
# variable: start — line 171
# variable: reply — line 172
# variable: data — line 174
# variable: renewable — line 177
# variable: ttl — line 177
# END CODE MAP

from __future__ import annotations

import http.client
import json
import re
import ssl
import time
from collections.abc import Callable
from pathlib import Path
from urllib.parse import urlsplit

from rotation.contracts import Lease, ProviderError, secret

MAX_BODY = 65536


def unique(pairs: list[tuple[str, object]]) -> dict[str, object]:
    """Reject ambiguous duplicate JSON keys rather than letting the last credential field win."""
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key")
        result[key] = value
    return result


def invalid_constant(value: str) -> object:
    """Reject JSON NaN/Infinity without reflecting raw provider content."""
    raise ValueError("invalid JSON constant")


class Transport:
    """Deliberately loopback-only lab HTTP API; caller supplies a trusted certificate file, not an insecure toggle."""

    def __init__(self, endpoint: str, ca: Path, token: str = "") -> None:
        """Validate a numeric loopback HTTPS URL/token and build a standard certificate-verifying context."""
        parsed = urlsplit(endpoint)
        if (
            parsed.scheme != "https"
            or parsed.hostname != "127.0.0.1"
            or parsed.username
            or parsed.password
            or parsed.path not in ("", "/")
            or parsed.query
            or parsed.fragment
            or not parsed.port
        ):
            raise ValueError("loopback HTTPS endpoint required")
        if token:
            secret(token)
        self.port = parsed.port
        self._token = token
        self._context = ssl.create_default_context(cafile=str(ca))
        self._context.minimum_version = ssl.TLSVersion.TLSv1_2

    def request(
        self, method: str, path: str, body: dict[str, object] | None = None
    ) -> dict[str, object]:
        """Use a two-second socket-operation timeout, cap JSON bytes, suppress raw errors, and close transport."""
        if (
            method not in {"GET", "POST", "PUT"}
            or not re.fullmatch(r"[A-Za-z0-9_/-]{1,256}", path)
            or "//" in path
        ):
            raise ValueError("invalid API operation")
        payload = (
            json.dumps(body, allow_nan=False).encode() if body is not None else None
        )
        if payload is not None and len(payload) > MAX_BODY:
            raise ValueError("request exceeds byte cap")
        connection = http.client.HTTPSConnection(
            "127.0.0.1", self.port, context=self._context, timeout=2
        )
        try:
            connection.request(
                method,
                "/v1/" + path,
                body=payload,
                headers={
                    "X-Vault-Token": self._token,
                    "Content-Type": "application/json",
                },
            )
            response = connection.getresponse()
            if response.status in {401, 403}:
                raise ProviderError("denied")
            if response.status == 429 or response.status >= 500:
                raise ProviderError("unavailable", True)
            if response.status not in {200, 204}:
                raise ProviderError("invalid")
            raw = response.read(MAX_BODY + 1)
            if len(raw) > MAX_BODY:
                raise ProviderError("invalid")
            if not raw and response.status == 204:
                return {}
            result: object = json.loads(
                raw, object_pairs_hook=unique, parse_constant=invalid_constant
            )
            if not isinstance(result, dict):
                raise ProviderError("invalid")
            return result
        except ssl.SSLError:
            raise ProviderError("tls") from None
        except (OSError, http.client.HTTPException):
            raise ProviderError("unavailable", True) from None
        except (ValueError, UnicodeError, RecursionError):
            raise ProviderError("invalid") from None
        finally:
            connection.close()


class BaoProvider:
    """Obtain a fixed reader dynamic credential; no root/admin operations are exposed by this adapter."""

    def __init__(
        self, transport: Transport, clock: Callable[[], float] = time.monotonic
    ) -> None:
        """Hold the scoped TLS transport and monotonic clock; lease lifetime begins before the request."""
        self.transport = transport
        self.clock = clock

    def issue(self) -> Lease:
        """Validate provider-issued fields and TTL; unexpected/unsafe data becomes a non-retryable safe error."""
        start = self.clock()
        reply = self.transport.request("GET", "database/creds/reader")
        try:
            data = reply["data"]
            if not isinstance(data, dict):
                raise ValueError("invalid credential payload")
            ttl, renewable = reply["lease_duration"], reply["renewable"]
            if type(ttl) is not int or type(renewable) is not bool:
                raise ValueError("invalid lifetime")
            return Lease(
                secret(reply["lease_id"]),
                secret(data["username"], 128),
                secret(data["password"]),
                start,
                ttl,
                renewable,
            )
        except (KeyError, TypeError, ValueError):
            raise ProviderError("invalid") from None
