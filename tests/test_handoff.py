"""Real portable broker/coordinator consumer handoff, replay, outage and privacy tests. Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# definition: fixture — line 81
# variable: clock — line 83
# variable: provider — line 84
# variable: broker — line 85
# definition: test_generation_is_not_consumer_acceptance — line 89
# variable: _ — line 91
# variable: clock — line 91
# variable: coordinator — line 91
# variable: first — line 94
# variable: first_generation — line 94
# variable: current — line 106
# variable: generation — line 106
# variable: row — line 113
# definition: test_concurrent_drained_acknowledgements — line 120
# variable: _ — line 122
# variable: coordinator — line 122
# variable: provider — line 122
# definition: accept — line 125
# parameter: code — line 125
# variable: generation — line 127
# variable: lease — line 127
# variable: pool — line 130
# variable: result — line 132
# definition: test_bad_acknowledgements_fail — line 151
# parameter: bad — line 151
# variable: _ — line 153
# variable: clock — line 153
# variable: coordinator — line 153
# variable: generation — line 157
# variable: lease — line 157
# variable: code — line 158
# variable: drained — line 158
# variable: code — line 160
# variable: code — line 162
# variable: generation — line 164
# variable: generation — line 166
# variable: drained — line 168
# definition: test_outage_fallback_denial_and_generation_bound — line 185
# variable: clock — line 187
# variable: coordinator — line 187
# variable: provider — line 187
# attribute: errors — line 189
# attribute: errors — line 191
# attribute: _generation — line 198
# definition: test_consumer_bounds — line 209
# parameter: codes — line 209
# variable: _ — line 211
# variable: coordinator — line 211
# definition: test_actual_demo_and_cli — line 216
# parameter: tmp_path — line 216
# variable: result — line 218
# variable: row — line 219
# variable: row — line 220
# variable: row — line 230
# variable: text — line 233
# variable: value — line 236
# variable: output — line 244
# variable: completed — line 245
# definition: main_with_output — line 259
# parameter: output — line 259
# END CODE MAP

import json
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from unittest.mock import patch

import pytest

from rotation.__main__ import main
from rotation.broker import Broker
from rotation.contracts import Policy, ProviderError, Unavailable
from rotation.handoff import Coordinator, demonstrate, publish
from rotation.simulation import Clock, Scripted


def fixture() -> tuple[Coordinator, Clock, Scripted]:
    """Build actual core state with an explicitly fictional provider and virtual monotonic clock."""
    clock = Clock()
    provider = Scripted(clock)
    broker = Broker(provider, Policy(), clock=clock, sleep=clock.sleep)
    return Coordinator(broker, ("api", "batch", "report")), clock, provider


def test_generation_is_not_consumer_acceptance() -> None:
    """One broker issue does not mean all consumers switched or drained their previous sessions."""
    coordinator, clock, _ = fixture()
    assert not coordinator.status()["all_consumers_acknowledged"]
    assert coordinator.refresh() == 1
    first_generation, first = coordinator.request("api")
    coordinator.acknowledge(
        "api", first_generation, first, old_connections_drained=True
    )
    assert not coordinator.status()["all_consumers_acknowledged"]
    clock.sleep(6)
    assert coordinator.refresh() == 2
    with pytest.raises(ValueError):
        coordinator.acknowledge(
            "api", first_generation, first, old_connections_drained=True
        )
    coordinator.invalidate("api", first)
    generation, current = coordinator.request("api")
    assert current is not first and generation == 2
    assert coordinator.status()["previous_overlap_usable"]
    clock.sleep(3)
    assert not coordinator.status()["previous_overlap_usable"]
    assert coordinator.status()["current_lease_usable"]
    assert all(
        not row["current_acknowledged"] for row in coordinator.status()["consumers"]
    )
    coordinator.invalidate("api", current)
    with pytest.raises(Unavailable):
        coordinator.request("api")


def test_concurrent_drained_acknowledgements() -> None:
    """Concurrent consumers receive the identical generation; detached safe status does not mutate state."""
    coordinator, _, provider = fixture()
    coordinator.refresh()

    def accept(code: str) -> None:
        """Represent application code explicitly asserting its old owned pool was drained."""
        generation, lease = coordinator.request(code)
        coordinator.acknowledge(code, generation, lease, old_connections_drained=True)

    with ThreadPoolExecutor(max_workers=3) as pool:
        list(pool.map(accept, coordinator.consumers))
    result = coordinator.status()
    assert result["all_consumers_acknowledged"] and provider.count == 1
    result["consumers"][0]["current_acknowledged"] = False
    assert coordinator.status()["all_consumers_acknowledged"]


@pytest.mark.parametrize(
    "bad",
    [
        "unknown",
        "unrequested",
        "wrong-generation",
        "bool-generation",
        "undrained",
        "replay",
        "expired",
        "unknown-invalidation",
    ],
)
def test_bad_acknowledgements_fail(bad: str) -> None:
    """Only a fresh requested exact object/generation and explicit drained assertion can advance one consumer."""
    coordinator, clock, _ = fixture()
    with pytest.raises(Unavailable):
        coordinator.request("api")
    coordinator.refresh()
    generation, lease = coordinator.request("api")
    code, drained = "api", True
    if bad == "unknown":
        code = "outside"
    elif bad == "unrequested":
        code = "batch"
    elif bad == "wrong-generation":
        generation += 1
    elif bad == "bool-generation":
        generation = True
    elif bad == "undrained":
        drained = False
    elif bad == "replay":
        coordinator.acknowledge(code, generation, lease, old_connections_drained=True)
    elif bad == "expired":
        clock.sleep(10)
    else:
        with pytest.raises(ValueError):
            coordinator.invalidate("outside", lease)
        return
    with pytest.raises((ValueError, Unavailable)):
        coordinator.acknowledge(
            code, generation, lease, old_connections_drained=drained
        )
    with pytest.raises(ValueError):
        coordinator.request("outside")


def test_outage_fallback_denial_and_generation_bound() -> None:
    """Transient cached fallback preserves generation; hard denial and expiry cannot preserve availability."""
    coordinator, clock, provider = fixture()
    coordinator.refresh()
    provider.errors = [ProviderError("unavailable", True)] * 2
    assert coordinator.refresh() == 1
    provider.errors = [ProviderError("denied")]
    with pytest.raises(Unavailable):
        coordinator.refresh()
    assert not coordinator.status()["current_lease_usable"]
    with pytest.raises(Unavailable):
        coordinator.request("api")
    coordinator.refresh()
    coordinator._generation = 1000000
    with pytest.raises(Unavailable):
        coordinator.refresh()
    assert not coordinator.status()["current_lease_usable"]
    clock.sleep(10)
    assert not coordinator.status()["all_consumers_acknowledged"]


@pytest.mark.parametrize(
    "codes", [(), ("same", "same"), ("real user",), ("x",) * 33, ([],)]
)
def test_consumer_bounds(codes: tuple[str, ...]) -> None:
    """Unknown/free-form identities cannot enter a status report or create an unbounded consumer map."""
    coordinator, _, _ = fixture()
    with pytest.raises(ValueError):
        Coordinator(coordinator.broker, codes)


def test_actual_demo_and_cli(tmp_path: Path) -> None:
    """Virtual operational timeline explicitly distinguishes partial rotation, overlap expiry and recovery."""
    result = demonstrate()
    assert [row["generation"] for row in result["timeline"]] == [1, 2, 2, 2, 3]
    assert [row["all_consumers_acknowledged"] for row in result["timeline"]] == [
        True,
        False,
        False,
        False,
        True,
    ]
    assert not result["timeline"][2]["previous_overlap_usable"]
    assert [
        row["acknowledged_lifetime_window_open"]
        for row in result["timeline"][2]["consumers"]
    ] == [True, False, False]
    assert not result["timeline"][3]["current_lease_usable"]
    text = json.dumps(result)
    assert not any(
        value in text
        for value in (
            "database/creds/reader",
            "fictional-",
            "not-a-real-database-credential",
            '"password"',
            '"lease_id"',
        )
    )
    output = tmp_path / "demo"
    completed = subprocess.run(
        [sys.executable, "-m", "rotation", "handoff-demo", "--output", str(output)],
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    assert completed.returncode == 0 and "no credentials exported" in completed.stdout
    assert (output / "handoff.json").is_file()
    assert main_with_output(output) == 2
    with pytest.raises(OSError):
        publish(result, tmp_path / "absent/new")


def main_with_output(output: Path) -> int:
    """Call the real main with explicit arguments without changing process arguments globally."""
    with patch("sys.argv", ["rotation", "handoff-demo", "--output", str(output)]):
        return main()
