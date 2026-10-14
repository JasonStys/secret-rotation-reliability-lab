"""Deterministic retry/expiry/identity/race tests plus actual concurrent single-flight threads. Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# definition: setup — line 61
# parameter: policy — line 61
# variable: clock — line 63
# variable: provider — line 64
# definition: test_refresh_and_invalidation — line 68
# variable: broker — line 70
# variable: clock — line 70
# variable: provider — line 70
# variable: first — line 71
# variable: second — line 74
# variable: stats — line 80
# definition: test_nontransient_drops_valid_cache — line 89
# parameter: kind — line 89
# variable: broker — line 91
# variable: clock — line 91
# variable: provider — line 91
# variable: old — line 92
# attribute: errors — line 93
# variable: result — line 94
# definition: test_retry_fallback_then_expiry — line 101
# variable: broker — line 103
# variable: clock — line 103
# variable: provider — line 103
# variable: first — line 104
# attribute: errors — line 105
# variable: good — line 107
# attribute: errors — line 108
# attribute: errors — line 111
# definition: test_capped_retry_delays_without_cache — line 118
# variable: broker — line 120
# variable: clock — line 120
# variable: provider — line 120
# attribute: errors — line 121
# definition: test_invalid_candidate_never_cached — line 135
# parameter: bad — line 135
# variable: broker — line 137
# variable: clock — line 137
# variable: provider — line 137
# attribute: issue — line 139
# definition: test_single_flight_threads — line 144
# variable: broker — line 146
# variable: clock — line 146
# variable: provider — line 146
# variable: pool — line 147
# parameter: _ — line 148
# variable: values — line 148
# variable: value — line 149
# END CODE MAP

from concurrent.futures import ThreadPoolExecutor

import pytest

from rotation.broker import Broker
from rotation.contracts import Lease, Policy, ProviderError, Unavailable
from rotation.simulation import Clock, Scripted


def setup(policy=None):
    """Create an independently controlled clock/provider/broker for one test."""
    clock = Clock()
    provider = Scripted(clock)
    return clock, provider, Broker(provider, policy, clock=clock, sleep=clock.sleep)


def test_refresh_and_invalidation():
    """A late old-generation invalidation cannot erase a newer lease; exact current failure can."""
    clock, provider, broker = setup()
    first = broker.get()
    assert broker.get() is first
    clock.sleep(6)
    second = broker.get()
    assert second is not first
    broker.invalidate(first)
    assert broker.get() is second
    broker.invalidate(second)
    assert broker.get() is not second
    stats = broker.stats()
    assert stats["issues"] == 3 and stats["invalidations"] == 1 and provider.count == 3
    stats["issues"] = 999
    assert broker.stats()["issues"] == 3
    with pytest.raises(ValueError):
        broker.get(force=1)


@pytest.mark.parametrize("kind", ["denied", "tls", "invalid"])
def test_nontransient_drops_valid_cache(kind):
    """Authorization/malformed/TLS failures cannot hide behind a still-valid old credential."""
    clock, provider, broker = setup()
    old = broker.get()
    provider.errors = [ProviderError(kind)]
    with pytest.raises(Unavailable, match="refused") as result:
        broker.get(force=True)
    assert result.value.__suppress_context__ and provider.count == 2
    assert broker.stats()["denials"] == 1
    assert broker.get() is not old


def test_retry_fallback_then_expiry():
    """Real retry elapsed time is rechecked before fallback; expired leases cannot be returned."""
    clock, provider, broker = setup()
    first = broker.get()
    provider.errors = [ProviderError("unavailable", True)]
    assert broker.get(force=True) is not first
    good = broker.get()
    provider.errors = [ProviderError("unavailable", True)] * 2
    assert broker.get(force=True) is good and broker.stats()["fallbacks"] == 1
    clock.sleep(8.95)
    provider.errors = [ProviderError("unavailable", True)] * 2
    with pytest.raises(Unavailable, match="no usable"):
        broker.get(force=True)
    assert provider.count == 7 and broker.stats()["fallbacks"] == 1
    assert broker.get() is not good


def test_capped_retry_delays_without_cache():
    """Three attempts incur only two capped sleeps, then stop with no credential fallback."""
    clock, provider, broker = setup(Policy(attempts=3, base_delay=0.2, max_delay=0.2))
    provider.errors = [ProviderError("unavailable", True)] * 3
    with pytest.raises(Unavailable):
        broker.get()
    assert provider.count == 3 and clock.now == pytest.approx(100.4)


@pytest.mark.parametrize(
    "bad",
    [
        None,
        "credential",
        Lease("database/creds/reader/a", "user", "password", 0, 3, True),
    ],
)
def test_invalid_candidate_never_cached(bad):
    """A malformed/expired provider candidate cannot replace or permit fallback to an existing lease."""
    clock, provider, broker = setup()
    broker.get()
    provider.issue = lambda: bad
    with pytest.raises(Unavailable, match="refused"):
        broker.get(force=True)


def test_single_flight_threads():
    """Thirty-two simultaneous native requests share one issue, not thirty-two manager credentials."""
    clock, provider, broker = setup()
    with ThreadPoolExecutor(max_workers=8) as pool:
        values = list(pool.map(lambda _: broker.get(), range(32)))
    assert all(value is values[0] for value in values)
    assert provider.count == 1 and broker.stats()["requests"] == 32
