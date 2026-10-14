"""Single-flight credential refresh with bounded retry, safe statistics and stale-lease guards. Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# definition: Provider — line 47
# definition: issue — line 50
# parameter: self — line 50
# definition: Broker — line 55
# definition: __init__ — line 58
# parameter: self — line 59
# parameter: provider — line 60
# parameter: policy — line 61
# parameter: clock — line 63
# parameter: sleep — line 64
# attribute: provider — line 67
# attribute: policy — line 68
# attribute: clock — line 69
# attribute: sleep — line 70
# attribute: _lock — line 71
# attribute: _lease — line 72
# attribute: _counts — line 73
# definition: get — line 82
# parameter: force — line 82
# parameter: self — line 82
# variable: now — line 88
# variable: attempt — line 95
# variable: candidate — line 98
# attribute: _lease — line 105
# attribute: _lease — line 117
# attribute: _lease — line 126
# definition: invalidate — line 129
# parameter: observed — line 129
# parameter: self — line 129
# attribute: _lease — line 133
# definition: stats — line 136
# parameter: self — line 136
# END CODE MAP

from __future__ import annotations

import threading
import time
from collections.abc import Callable
from typing import Protocol

from rotation.contracts import Lease, Policy, ProviderError, Unavailable


class Provider(Protocol):
    """A provider must implement issue with its own bounded transport timeout."""

    def issue(self) -> Lease:
        """Return a validated lease timed from request initiation, or raise a safe ProviderError."""
        ...


class Broker:
    """Serialize refresh so concurrent consumers share one lease; callers must close old database connections."""

    def __init__(
        self,
        provider: Provider,
        policy: Policy | None = None,
        *,
        clock: Callable[[], float] = time.monotonic,
        sleep: Callable[[float], None] = time.sleep,
    ) -> None:
        """Inject provider/policy and testable monotonic clock/sleeper; no credentials are written to disk."""
        self.provider = provider
        self.policy = policy if policy is not None else Policy()
        self.clock = clock
        self.sleep = sleep
        self._lock = threading.Lock()
        self._lease: Lease | None = None
        self._counts = {
            "requests": 0,
            "issues": 0,
            "attempts": 0,
            "fallbacks": 0,
            "denials": 0,
            "invalidations": 0,
        }

    def get(self, *, force: bool = False) -> Lease:
        """Refresh if due/forced. Only transient failures permit still-valid cached credentials, never expired ones."""
        if type(force) is not bool:
            raise ValueError("force must be bool")
        with self._lock:
            self._counts["requests"] += 1
            now = self.clock()
            if (
                self._lease
                and not force
                and not self._lease.refresh_due(now, self.policy)
            ):
                return self._lease
            for attempt in range(self.policy.attempts):
                self._counts["attempts"] += 1
                try:
                    candidate = self.provider.issue()
                    if not isinstance(candidate, Lease) or not candidate.usable(
                        self.clock(), self.policy.expiry_guard
                    ):
                        raise ProviderError("invalid")
                except ProviderError as error:
                    if not error.retryable:
                        self._lease = None
                        self._counts["denials"] += 1
                        raise Unavailable("credential refresh refused") from None
                    if attempt + 1 < self.policy.attempts:
                        self.sleep(
                            min(
                                self.policy.base_delay * 2**attempt,
                                self.policy.max_delay,
                            )
                        )
                        continue
                else:
                    self._lease = candidate
                    self._counts["issues"] += 1
                    return candidate
            # Recheck the clock AFTER retry/transport time; never reuse a pre-request expiry decision.
            if self._lease and self._lease.usable(
                self.clock(), self.policy.expiry_guard
            ):
                self._counts["fallbacks"] += 1
                return self._lease
            self._lease = None
            raise Unavailable("no usable credentials") from None

    def invalidate(self, observed: Lease) -> None:
        """Invalidate only the exact lease that failed; a late failure cannot erase a newer generation."""
        with self._lock:
            if self._lease is observed:
                self._lease = None
                self._counts["invalidations"] += 1

    def stats(self) -> dict[str, int]:
        """Return a detached allowlisted counter snapshot, with no credential identifiers."""
        with self._lock:
            return self._counts.copy()
