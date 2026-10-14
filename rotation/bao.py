"""Verified TLS, no redirects/proxies, bounded OpenBao JSON and safe provider errors. Created by Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# variable: MAX_BODY — line 74
# definition: unique — line 77
# parameter: pairs — line 77
# variable: result — line 79
# variable: key — line 80
# variable: value — line 80
# definition: invalid_constant — line 87
# parameter: value — line 87
# definition: Transport — line 92
# definition: __init__ — line 95
# parameter: ca — line 95
# parameter: endpoint — line 95
# parameter: self — line 95
# parameter: token — line 95
# variable: parsed — line 97
# attribute: port — line 111
# attribute: _token — line 112
# attribute: response_status — line 113
# attribute: response_stage — line 114
# attribute: response_flags — line 115
# attribute: _context — line 116
# attribute: minimum_version — line 117
# definition: request — line 119
# parameter: body — line 120
# parameter: method — line 120
# parameter: path — line 120
# parameter: self — line 120
# variable: payload — line 129
# variable: connection — line 134
# attribute: response_flags — line 137
# attribute: response_stage — line 137
# attribute: response_status — line 137
# variable: response — line 148
# attribute: response_status — line 149
# variable: failure_body — line 152
# attribute: response_flags — line 153
# variable: label — line 155
# variable: phrase — line 155
# variable: raw — line 175
# attribute: response_stage — line 176
# variable: result — line 181
# attribute: response_stage — line 184
# definition: BaoProvider — line 198
# definition: __init__ — line 201
# parameter: clock — line 202
# parameter: self — line 202
# parameter: transport — line 202
# attribute: transport — line 205
# attribute: clock — line 206
# definition: issue — line 208
# parameter: self — line 208
# variable: start — line 210
# variable: reply — line 211
# variable: data — line 213
# variable: renewable — line 216
# variable: ttl — line 216
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
        self.response_status = 0
        self.response_stage = "idle"
        self.response_flags: list[str] = []
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
        self.response_status, self.response_stage, self.response_flags = 0, "status", []
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
            self.response_status = response.status
            if response.status >= 400:
                # Only fixed presence labels survive. No raw backend message/body is stored or logged.
                failure_body = response.read(MAX_BODY + 1).lower()
                self.response_flags = [
                    label
                    for phrase, label in [
                        (b"permission denied", "permission"),
                        (b"unsupported", "unsupported"),
                        (b"audit", "audit"),
                        (b"file", "file"),
                        (b"format", "format"),
                        (b"parse", "parse"),
                        (b"invalid", "invalid"),
                        (b"failed", "failed"),
                        (b"exists", "exists"),
                        (b"cannot enable audit device via api", "audit-api-disabled"),
                    ]
                    if phrase in failure_body
                ]
            if response.status in {401, 403}:
                raise ProviderError("denied")
            if response.status == 429 or response.status >= 500:
                raise ProviderError("unavailable", True)
            if response.status not in {200, 204}:
                raise ProviderError("invalid")
            raw = response.read(MAX_BODY + 1)
            self.response_stage = "body"
            if len(raw) > MAX_BODY:
                raise ProviderError("invalid")
            if not raw and response.status == 204:
                return {}
            result: object = json.loads(
                raw, object_pairs_hook=unique, parse_constant=invalid_constant
            )
            self.response_stage = "object"
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
