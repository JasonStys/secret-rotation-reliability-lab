"""Bounded lease/policy contracts; secret fields never enter representations. Created by Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# definition: number — line 57
# parameter: lower — line 57
# parameter: upper — line 57
# parameter: value — line 57
# variable: numeric — line 61
# definition: secret — line 67
# parameter: maximum — line 67
# parameter: value — line 67
# variable: c — line 72
# definition: Policy — line 79
# variable: refresh_fraction — line 82
# variable: expiry_guard — line 83
# variable: attempts — line 84
# variable: base_delay — line 85
# variable: max_delay — line 86
# definition: __post_init__ — line 88
# parameter: self — line 88
# definition: Lease — line 99
# variable: lease_id — line 102
# variable: username — line 103
# variable: password — line 104
# variable: started_at — line 105
# variable: ttl — line 106
# variable: renewable — line 107
# definition: __post_init__ — line 109
# parameter: self — line 109
# definition: __repr__ — line 126
# parameter: self — line 126
# definition: usable — line 132
# parameter: guard — line 132
# parameter: now — line 132
# parameter: self — line 132
# definition: refresh_due — line 138
# parameter: now — line 138
# parameter: policy — line 138
# parameter: self — line 138
# definition: ProviderError — line 146
# definition: __init__ — line 149
# parameter: category — line 149
# parameter: retryable — line 149
# parameter: self — line 149
# attribute: category — line 157
# attribute: retryable — line 158
# definition: Unavailable — line 162
# END CODE MAP

from __future__ import annotations

import math
import re
from dataclasses import dataclass, field
from typing import cast


def number(value: object, lower: float, upper: float) -> float:
    """Validate finite non-bool numeric input within inclusive bounds; return a float."""
    if type(value) not in (int, float):
        raise ValueError("numeric boundary violated")
    numeric = cast(int | float, value)
    if not math.isfinite(numeric) or not lower <= numeric <= upper:
        raise ValueError("numeric boundary violated")
    return float(numeric)


def secret(value: object, maximum: int = 512) -> str:
    """Accept bounded nonempty printable ASCII; never include rejected content in errors."""
    if (
        not isinstance(value, str)
        or not 1 <= len(value) <= maximum
        or any(not 33 <= ord(c) <= 126 for c in value)
    ):
        raise ValueError("invalid credential field")
    return value


@dataclass(frozen=True)
class Policy:
    """Refresh early, retry finitely, and stop before expiry; parameters are seconds/fraction/count."""

    refresh_fraction: float = 0.6
    expiry_guard: float = 1.0
    attempts: int = 2
    base_delay: float = 0.05
    max_delay: float = 0.2

    def __post_init__(self) -> None:
        """Reject unsafe ranges, bool counts, nonfinite numbers and inverted retry limits."""
        number(self.refresh_fraction, 0.1, 0.9)
        number(self.expiry_guard, 0.1, 30)
        number(self.base_delay, 0, 1)
        number(self.max_delay, self.base_delay, 2)
        if type(self.attempts) is not int or not 1 <= self.attempts <= 3:
            raise ValueError("attempt count must be 1..3")


@dataclass(frozen=True, repr=False)
class Lease:
    """In-memory credentials plus conservative monotonic lifetime; no serializable public secret record."""

    lease_id: str = field(repr=False)
    username: str = field(repr=False)
    password: str = field(repr=False)
    started_at: float
    ttl: int
    renewable: bool

    def __post_init__(self) -> None:
        """Require the fixed reader lease namespace, bounded ASCII credentials and valid lifetime."""
        secret(self.lease_id)
        if not re.fullmatch(
            r"database/creds/reader/[A-Za-z0-9_.-]{1,128}", self.lease_id
        ):
            raise ValueError("unexpected lease namespace")
        secret(self.username, 128)
        secret(self.password)
        number(self.started_at, 0, 1e12)
        if (
            type(self.ttl) is not int
            or not 3 <= self.ttl <= 3600
            or type(self.renewable) is not bool
        ):
            raise ValueError("invalid lease lifetime")

    def __repr__(self) -> str:
        """Expose lifetime metadata only, including when an exception/test framework formats the object."""
        return (
            f"Lease(ttl={self.ttl}, renewable={self.renewable}, credentials=<redacted>)"
        )

    def usable(self, now: float, guard: float) -> bool:
        """True only inside the conservative lifetime and strictly before the expiry guard."""
        number(now, 0, 1e12)
        number(guard, 0, 30)
        return self.started_at <= now < self.started_at + self.ttl - guard

    def refresh_due(self, now: float, policy: Policy) -> bool:
        """Refresh at the earlier fractional lifetime/expiry boundary; never accept clock rollback."""
        return not self.usable(now, policy.expiry_guard) or now >= min(
            self.started_at + self.ttl * policy.refresh_fraction,
            self.started_at + self.ttl - policy.expiry_guard,
        )


class ProviderError(Exception):
    """Only a safe category and retryability cross the provider boundary; raw provider messages are discarded."""

    def __init__(self, category: str, retryable: bool = False) -> None:
        """Allowlist categories; denied/invalid/TLS failures cannot be made retryable."""
        if (
            category not in {"unavailable", "denied", "invalid", "tls"}
            or type(retryable) is not bool
            or (retryable and category != "unavailable")
        ):
            raise ValueError("invalid provider error category")
        self.category = category
        self.retryable = retryable
        super().__init__(category)


class Unavailable(Exception):
    """Public fail-closed signal with no provider response, token, lease ID or database password."""
