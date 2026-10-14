"""Deterministic offline lifecycle demonstration, explicitly NOT live-manager evidence. Created by Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# definition: Clock — line 49
# definition: __init__ — line 52
# parameter: self — line 52
# attribute: now — line 54
# definition: __call__ — line 56
# parameter: self — line 56
# definition: sleep — line 60
# parameter: duration — line 60
# parameter: self — line 60
# attribute: now — line 62
# definition: Scripted — line 65
# definition: __init__ — line 68
# parameter: clock — line 68
# parameter: self — line 68
# attribute: clock — line 70
# attribute: count — line 71
# attribute: errors — line 72
# definition: issue — line 74
# parameter: self — line 74
# attribute: count — line 76
# definition: simulate — line 89
# parameter: source_sha — line 89
# variable: clock — line 91
# variable: provider — line 92
# variable: broker — line 93
# variable: cases — line 94
# variable: first — line 95
# variable: second — line 99
# attribute: errors — line 102
# variable: third — line 103
# attribute: errors — line 106
# attribute: errors — line 113
# variable: fourth — line 123
# attribute: errors — line 124
# variable: fifth — line 131
# END CODE MAP

from __future__ import annotations

from typing import Any

from rotation.broker import Broker
from rotation.contracts import Lease, Policy, ProviderError, Unavailable
from rotation.evidence import validate


class Clock:
    """Controlled monotonic seconds for repeatable offline tests; never changes the system clock."""

    def __init__(self) -> None:
        """Start at a fixed synthetic monotonic instant."""
        self.now = 100.0

    def __call__(self) -> float:
        """Return controlled seconds."""
        return self.now

    def sleep(self, duration: float) -> None:
        """Advance simulated time instead of blocking."""
        self.now += duration


class Scripted:
    """Synthetic provider with no network/storage credentials; safe failure types can be injected."""

    def __init__(self, clock: Clock) -> None:
        """Hold controlled time and an initial successful issue sequence."""
        self.clock = clock
        self.count = 0
        self.errors: list[ProviderError] = []

    def issue(self) -> Lease:
        """Return a fresh fictional reader lease or consume one explicitly injected safe error."""
        self.count += 1
        if self.errors:
            raise self.errors.pop(0)
        return Lease(
            f"database/creds/reader/demo-{self.count}",
            f"fictional-{self.count}",
            "not-a-real-database-credential",
            self.clock(),
            10,
            True,
        )


def simulate(source_sha: str) -> dict[str, Any]:
    """Assert eight lifecycle oracles and return a schema-checked, explicitly simulated aggregate."""
    clock = Clock()
    provider = Scripted(clock)
    broker = Broker(provider, Policy(), clock=clock, sleep=clock.sleep)
    cases = []
    first = broker.get()
    assert broker.get() is first and provider.count == 1
    cases.append({"name": "cache", "passed": True, "duration_ms": 0})
    clock.sleep(6)
    second = broker.get()
    assert second is not first
    cases.append({"name": "rotation", "passed": True, "duration_ms": 0})
    provider.errors = [ProviderError("unavailable", True)]
    third = broker.get(force=True)
    assert third is not second
    cases.append({"name": "retry", "passed": True, "duration_ms": 50})
    provider.errors = [
        ProviderError("unavailable", True),
        ProviderError("unavailable", True),
    ]
    assert broker.get(force=True) is third
    cases.append({"name": "grace", "passed": True, "duration_ms": 50})
    clock.sleep(10)
    provider.errors = [
        ProviderError("unavailable", True),
        ProviderError("unavailable", True),
    ]
    try:
        broker.get()
    except Unavailable:
        cases.append({"name": "expiry", "passed": True, "duration_ms": 50})
    else:
        raise AssertionError("expired credential returned")
    fourth = broker.get()
    provider.errors = [ProviderError("denied")]
    try:
        broker.get(force=True)
    except Unavailable:
        cases.append({"name": "denied", "passed": True, "duration_ms": 0})
    else:
        raise AssertionError("denied identity reused credentials")
    fifth = broker.get()
    broker.invalidate(fourth)
    assert broker.get() is fifth
    cases.append({"name": "stale_invalidation", "passed": True, "duration_ms": 0})
    assert fifth.password not in repr(fifth) and fifth.username not in repr(fifth)
    cases.append({"name": "redaction", "passed": True, "duration_ms": 0})
    return validate(
        {
            "schema": 1,
            "mode": "simulation",
            "source_sha": source_sha,
            "cases": cases,
            "metrics": broker.stats(),
        }
    )
