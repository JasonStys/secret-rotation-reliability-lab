"""Generation-bound multi-consumer acknowledgements; credentials never enter status. Created by Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# definition: Coordinator — line 93
# definition: __init__ — line 96
# parameter: broker — line 96
# parameter: consumers — line 96
# parameter: self — line 96
# variable: code — line 103
# attribute: broker — line 108
# attribute: consumers — line 109
# attribute: _lock — line 110
# attribute: _current — line 111
# attribute: _previous — line 112
# attribute: _generation — line 113
# attribute: _available — line 114
# attribute: _requests — line 115
# attribute: _acks — line 116
# attribute: _accepted_windows — line 117
# definition: refresh — line 121
# parameter: self — line 121
# variable: candidate — line 125
# attribute: _available — line 127
# attribute: _available — line 131
# attribute: _current — line 133
# attribute: _previous — line 133
# attribute: _generation — line 134
# attribute: _available — line 135
# definition: request — line 138
# parameter: consumer — line 138
# parameter: self — line 138
# definition: acknowledge — line 154
# parameter: self — line 155
# parameter: consumer — line 156
# parameter: generation — line 157
# parameter: observed — line 158
# parameter: old_connections_drained — line 160
# definition: status — line 191
# parameter: self — line 191
# variable: now — line 194
# variable: usable — line 195
# variable: previous_usable — line 200
# variable: consumers — line 203
# variable: code — line 204
# variable: window — line 205
# variable: row — line 227
# definition: invalidate — line 233
# parameter: consumer — line 233
# parameter: observed — line 233
# parameter: self — line 233
# attribute: _available — line 240
# definition: demonstrate — line 243
# variable: clock — line 245
# variable: provider — line 246
# variable: broker — line 247
# variable: coordinator — line 248
# variable: timeline — line 249
# variable: consumer — line 251
# variable: generation — line 252
# variable: lease — line 252
# variable: generation — line 259
# variable: lease — line 259
# attribute: errors — line 265
# attribute: errors — line 274
# variable: consumer — line 286
# variable: generation — line 287
# variable: lease — line 287
# definition: publish — line 302
# parameter: output — line 302
# parameter: result — line 302
# variable: absolute — line 304
# variable: part — line 307
# variable: text — line 310
# variable: rows — line 311
# variable: key — line 315
# variable: row — line 324
# variable: page — line 326
# END CODE MAP

from __future__ import annotations

import html
import json
import re
import threading
from pathlib import Path
from typing import Any

from rotation.broker import Broker
from rotation.contracts import Lease, Policy, ProviderError, Unavailable
from rotation.simulation import Clock, Scripted


class Coordinator:
    """Track declared consumers separately from broker refresh; acknowledgements assert drained old connections."""

    def __init__(self, broker: Broker, consumers: tuple[str, ...]) -> None:
        """Own one broker's consumer handoff with1..32 unique nonidentifying consumer codes."""
        if (
            not 1 <= len(consumers) <= 32
            or any(
                not isinstance(code, str)
                or re.fullmatch(r"[a-z][a-z0-9-]{0,47}", code) is None
                for code in consumers
            )
            or len(set(consumers)) != len(consumers)
        ):
            raise ValueError("consumer contract failed")
        self.broker = broker
        self.consumers = tuple(sorted(consumers))
        self._lock = threading.Lock()
        self._current: Lease | None = None
        self._previous: Lease | None = None
        self._generation = 0
        self._available = False
        self._requests = dict.fromkeys(consumers, 0)
        self._acks = dict.fromkeys(consumers, 0)
        self._accepted_windows: dict[str, tuple[float, float] | None] = dict.fromkeys(
            consumers
        )

    def refresh(self) -> int:
        """Refresh via unchanged broker; fallback to same valid object never invents a new generation."""
        with self._lock:
            try:
                candidate = self.broker.get(force=True)
            except Unavailable:
                self._available = False
                raise
            if candidate is not self._current:
                if self._generation >= 1000000:
                    self._available = False
                    raise Unavailable("generation bound reached")
                self._previous, self._current = self._current, candidate
                self._generation += 1
            self._available = True
            return self._generation

    def request(self, consumer: str) -> tuple[int, Lease]:
        """Return current in-memory lease only to a declared consumer, within guard; do not acknowledge automatically."""
        with self._lock:
            if not isinstance(consumer, str) or consumer not in self._requests:
                raise ValueError("unknown consumer")
            if (
                not self._available
                or self._current is None
                or not self._current.usable(
                    self.broker.clock(), self.broker.policy.expiry_guard
                )
            ):
                raise Unavailable("no current usable handoff")
            self._requests[consumer] = self._generation
            return self._generation, self._current

    def acknowledge(
        self,
        consumer: str,
        generation: int,
        observed: Lease,
        *,
        old_connections_drained: bool,
    ) -> None:
        """Accept one requested exact current object/generation acknowledgement; stale/replayed/undrained requests fail."""
        with self._lock:
            if not isinstance(consumer, str) or consumer not in self._acks:
                raise ValueError("unknown consumer")
            if (
                type(generation) is not int
                or generation != self._generation
                or observed is not self._current
                or self._requests[consumer] != generation
                or self._acks[consumer] == generation
                or old_connections_drained is not True
            ):
                raise ValueError("handoff acknowledgement rejected")
            if (
                not self._available
                or self._current is None
                or not self._current.usable(
                    self.broker.clock(), self.broker.policy.expiry_guard
                )
            ):
                raise Unavailable("handoff lease no longer usable")
            self._acks[consumer] = generation
            self._accepted_windows[consumer] = (
                self._current.started_at,
                self._current.started_at
                + self._current.ttl
                - self.broker.policy.expiry_guard,
            )

    def status(self) -> dict[str, Any]:
        """Expose bounded detached consumer/generation/lifetime metadata, never lease IDs or secret fields."""
        with self._lock:
            now = self.broker.clock()
            usable = (
                self._available
                and self._current is not None
                and self._current.usable(now, self.broker.policy.expiry_guard)
            )
            previous_usable = self._previous is not None and self._previous.usable(
                now, self.broker.policy.expiry_guard
            )
            consumers = []
            for code in self.consumers:
                window = self._accepted_windows[code]
                consumers.append(
                    {
                        "consumer": code,
                        "requested_generation": self._requests[code],
                        "acknowledged_generation": self._acks[code],
                        "current_acknowledged": bool(
                            usable and self._acks[code] == self._generation
                        ),
                        "acknowledged_lifetime_window_open": bool(
                            window is not None and window[0] <= now < window[1]
                        ),
                        "action": "none"
                        if usable and self._acks[code] == self._generation
                        else "obtain_usable_lease_then_drain_old_connections_and_acknowledge",
                    }
                )
            return {
                "generation": self._generation,
                "current_lease_usable": bool(usable),
                "previous_overlap_usable": bool(previous_usable),
                "all_consumers_acknowledged": all(
                    row["current_acknowledged"] for row in consumers
                ),
                "consumers": consumers,
                "limit": "Consumer identity and drained-connection acknowledgement are in-process assertions,not proof of database pool termination or server acceptance.",
            }

    def invalidate(self, consumer: str, observed: Lease) -> None:
        """Report exact failed credentials; late failures cannot block a newer handoff generation."""
        with self._lock:
            if not isinstance(consumer, str) or consumer not in self._requests:
                raise ValueError("unknown consumer")
            self.broker.invalidate(observed)
            if observed is self._current:
                self._available = False


def demonstrate() -> dict[str, Any]:
    """Exercise actual broker/coordinator with virtual time and a fictional provider,not a live secrets service."""
    clock = Clock()
    provider = Scripted(clock)
    broker = Broker(provider, Policy(), clock=clock, sleep=clock.sleep)
    coordinator = Coordinator(broker, ("api-reader", "batch-reader", "report-reader"))
    timeline = []
    coordinator.refresh()
    for consumer in coordinator.consumers:
        generation, lease = coordinator.request(consumer)
        coordinator.acknowledge(
            consumer, generation, lease, old_connections_drained=True
        )
    timeline.append({"step": "initial_handoff", **coordinator.status()})
    clock.sleep(6)
    coordinator.refresh()
    generation, lease = coordinator.request("api-reader")
    coordinator.acknowledge(
        "api-reader", generation, lease, old_connections_drained=True
    )
    timeline.append({"step": "partial_rotation", **coordinator.status()})
    clock.sleep(3)
    provider.errors = [
        ProviderError("unavailable", True),
        ProviderError("unavailable", True),
    ]
    assert coordinator.refresh() == generation
    timeline.append(
        {"step": "outage_valid_current_stale_consumers", **coordinator.status()}
    )
    clock.sleep(7)
    provider.errors = [
        ProviderError("unavailable", True),
        ProviderError("unavailable", True),
    ]
    try:
        coordinator.refresh()
    except Unavailable:
        pass
    else:
        raise AssertionError("expired lease accepted")
    timeline.append({"step": "outage_expired", **coordinator.status()})
    coordinator.refresh()
    for consumer in coordinator.consumers:
        generation, lease = coordinator.request(consumer)
        coordinator.acknowledge(
            consumer, generation, lease, old_connections_drained=True
        )
    timeline.append({"step": "recovery_handoff", **coordinator.status()})
    return {
        "schema": 1,
        "mode": "multi_consumer_simulation",
        "author": "Jason Stys",
        "timeline": timeline,
        "broker_counters": broker.stats(),
        "scope": "Virtual times,fictional credentials,actual portable broker/coordinator;no live manager/database/pool or zero-downtime guarantee.",
    }


def publish(result: dict[str, Any], output: Path) -> None:
    """Save bounded internally constructed credential-free demo metadata in new private JSON/inert HTML."""
    absolute = output.absolute()
    if any(
        part.is_symlink() or part.is_junction()
        for part in (absolute, *absolute.parents)
    ):
        raise ValueError("linked output refused")
    text = json.dumps(result, sort_keys=True, indent=2)
    rows = "".join(
        "<tr>"
        + "".join(
            f"<td>{html.escape(str(row[key]))}</td>"
            for key in (
                "step",
                "generation",
                "current_lease_usable",
                "previous_overlap_usable",
                "all_consumers_acknowledged",
            )
        )
        + "</tr>"
        for row in result["timeline"]
    )
    page = (
        '<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta http-equiv="Content-Security-Policy" content="default-src \'none\'; base-uri \'none\'; form-action \'none\'"><title>Consumer handoff — Jason Stys</title><main><h1>Multi-consumer credential handoff</h1><p>Created by Jason Stys. Explicit simulation; broker refresh is distinct from consumer acknowledgement.</p><table><caption>Virtual rotation/outage/recovery timeline</caption><tr><th>Step</th><th>Generation</th><th>Current usable</th><th>Previous overlap</th><th>All consumers acknowledged</th></tr>'
        + rows
        + "</table><details><summary>Consumer work queues and bounds</summary><pre>"
        + html.escape(text)
        + "</pre></details></main></html>"
    )
    absolute.mkdir(mode=0o700)
    (absolute / "handoff.json").write_text(text + "\n", encoding="utf-8")
    (absolute / "handoff.html").write_text(page, encoding="utf-8")
