"""Replay closed secret-free handoff scripts through the real Broker/Coordinator with virtual time. Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# variable: ROOT — line 135
# variable: PRODUCT — line 136
# variable: PROFILE — line 136
# variable: TITLE — line 137
# variable: VERSION — line 137
# variable: BANNER — line 138
# variable: COLUMNS — line 139
# variable: RESOURCES — line 145
# variable: RESOURCE_LIMITS — line 146
# variable: MODES — line 147
# variable: REVIEW_MODE — line 151
# variable: CHOICES — line 152
# variable: FIELDS — line 166
# variable: ACTIVE_FIELDS — line 175
# variable: SCENARIOS — line 193
# variable: HELP — line 205
# variable: POLICY_KEYS — line 209
# variable: EVENT_KEYS — line 216
# definition: closed — line 226
# parameter: fields — line 226
# parameter: value — line 226
# definition: code — line 233
# parameter: value — line 233
# definition: validate — line 243
# parameter: data — line 243
# variable: consumers — line 248
# variable: consumer — line 251
# variable: ttl — line 255
# variable: policy — line 258
# variable: events — line 259
# variable: requested — line 262
# variable: seconds — line 262
# variable: event — line 263
# variable: seconds — line 283
# definition: FictionalProvider — line 302
# definition: __init__ — line 305
# parameter: clock — line 305
# parameter: self — line 305
# parameter: ttl — line 305
# attribute: ttl — line 308
# definition: issue — line 310
# parameter: self — line 310
# definition: scenario — line 315
# parameter: name — line 315
# variable: _kind — line 321
# variable: _label — line 321
# variable: name — line 321
# definition: acknowledgements — line 326
# parameter: suffix — line 326
# variable: consumer — line 330
# variable: event — line 331
# definition: prepared — line 349
# parameter: name — line 349
# variable: events — line 353
# variable: events — line 358
# variable: events — line 376
# variable: events — line 389
# variable: events — line 394
# variable: events — line 399
# variable: events — line 410
# variable: events — line 428
# variable: event — line 437
# definition: replay — line 452
# parameter: data — line 452
# variable: policy — line 454
# variable: ttl — line 454
# variable: clock — line 455
# variable: provider — line 456
# variable: broker — line 457
# variable: coordinator — line 458
# variable: refs — line 459
# variable: timeline — line 460
# variable: event — line 461
# variable: index — line 461
# variable: observed — line 462
# variable: op — line 464
# attribute: errors — line 468
# variable: _ — line 475
# variable: generation — line 485
# variable: lease — line 485
# variable: observed — line 496
# variable: observed — line 498
# variable: final — line 512
# variable: row — line 517
# variable: row — line 518
# variable: row — line 522
# definition: analyze — line 530
# parameter: parameters — line 531
# parameter: stage — line 531
# parameter: state — line 531
# variable: mode — line 534
# variable: raw — line 537
# variable: data — line 542
# variable: original_policy — line 543
# variable: original_ttl — line 543
# variable: data — line 544
# variable: name — line 545
# variable: text — line 547
# variable: name — line 554
# variable: text — line 556
# variable: effective_policy — line 563
# variable: effective_ttl — line 563
# variable: result — line 564
# variable: scope — line 565
# definition: views — line 590
# parameter: files — line 590
# variable: r — line 592
# variable: row — line 595
# variable: row — line 599
# variable: row — line 603
# definition: cells — line 612
# parameter: row — line 612
# END CODE MAP

from __future__ import annotations

import copy
import hashlib
import re
import sys
from dataclasses import asdict, replace
from pathlib import Path
from typing import Any

from .broker import Broker
from .contracts import Lease, Policy, ProviderError, Unavailable, number
from .desktop_io import Rejected, canonical, json_value
from .desktop_state import Workspace
from .handoff import Coordinator
from .inputs import read_source
from .simulation import Clock, Scripted

ROOT = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parents[1]))
PRODUCT, PROFILE = "secret-rotation-reliability-lab", "SecretRotationReliabilityLab"
TITLE, VERSION = "Secret Rotation Rehearsal Workbench", "1.1.0"
BANNER = "Virtual in-process rehearsal only: no real credentials, OpenBao, database or pool termination."
COLUMNS = (
    "Step / consumer",
    "Expected / requested",
    "Observed / acknowledged",
    "Decision / action",
)
RESOURCES = ("notices.txt", "app.ico", "python314.dll")
RESOURCE_LIMITS: dict[str, int] = {}
MODES = (
    "Replay authorized secret-free handoff script",
    "Review prepared full-app rehearsal",
)
REVIEW_MODE = None
CHOICES = {
    "exercise": (
        "initial-handoff",
        "partial-rotation",
        "outage-grace",
        "outage-expired",
        "recovered",
        "denied",
        "stale-ack",
        "undrained-ack",
        "late-old-failure",
        "wrong-oracle",
    )
}
FIELDS = (
    ("script", "Authorized secret-free JSON rehearsal script", "file"),
    ("lease_ttl", "Optional fictional lease TTL, 3–3600 seconds", "text"),
    ("expiry_guard", "Optional expiry guard, 0.1–30 seconds", "text"),
    ("attempts", "Optional issue attempts, 1–3", "text"),
    ("base_delay", "Optional virtual initial retry delay, 0–1 second", "text"),
    ("max_delay", "Optional virtual maximum retry delay, 0–2 seconds", "text"),
    ("exercise", "Prepared full-app rehearsal", "choice"),
)
ACTIVE_FIELDS = {
    MODES[0]: (
        "script",
        "lease_ttl",
        "expiry_guard",
        "attempts",
        "base_delay",
        "max_delay",
    ),
    MODES[1]: (
        "exercise",
        "lease_ttl",
        "expiry_guard",
        "attempts",
        "base_delay",
        "max_delay",
    ),
}
SCENARIOS = (
    "Initial exact-generation handoff completes",
    "Partial rotation leaves two consumers pending",
    "Transient outage preserves only usable current lease",
    "Outage after expiry stays unavailable",
    "Recovery obtains and acknowledges a new generation",
    "Authorization denial invalidates cached credentials",
    "Late old-generation acknowledgement is rejected",
    "Undrained acknowledgement is rejected",
    "Late old-lease failure cannot erase current generation",
    "Wrong expected outcome stays a visible mismatch",
)
HELP = """Rehearse a bounded secret-free JSON event script using this project's actual Broker, Policy, Lease and Coordinator. Choose an authorized script or populate an editable prepared case. There is no provider URL, real token/password, arbitrary program, live OpenBao or database connection. The synthetic provider uses only the original fictional in-memory credentials; they are never returned, persisted, displayed or exported.
The script contains schema 1, one to 32 unique nonidentifying consumer codes, lease_ttl, a complete original Policy and one to 128 closed events. Operations: refresh; request(consumer,slot); acknowledge(consumer,slot,drained); invalidate(consumer,slot); advance(seconds); provider(category,count). Every event also has expect: ok/rejected/unavailable. Slot references bind the actual requested lease object and generation; no caller-supplied generation or lease identifier is accepted. Unknown consumers, stale/replayed references and false drain acknowledgements remain actual core rejections. Provider categories are none/unavailable/denied/invalid/tls, with at most 3 queued safe errors. No raw provider message is allowed.
Explicit optional guard/retry/TTL controls change only the effective rehearsal policy. The original script/policy is validated before changes. All statuses use a virtual monotonic clock; retry sleep advances that clock, never wall time. Refresh events intentionally call the original forced handoff refresh; the original Policy refresh_fraction is retained but this rehearsal does not measure automatic cached-get scheduling, concurrency, TLS or database-pool termination. The original broker/property/concurrency and live TLS drill remain separate mandatory gates.
Inspect expected versus actual outcomes, full per-step consumer/generation/lifetime status, final pending consumers and broker counters. A matching expected rejection is not successful authentication; a supplied drain flag remains an in-process assertion. A wrong oracle remains a visible mismatch. Search/filter retains the full denominator; exact export never overwrites. Sensitive selected paths/reports live in a trusted OS-owner plaintext profile, not encrypted or multiuser storage. Exit waits for the worker and durable commit."""
POLICY_KEYS = {
    "refresh_fraction",
    "expiry_guard",
    "attempts",
    "base_delay",
    "max_delay",
}
EVENT_KEYS = {
    "refresh": {"op", "expect"},
    "request": {"op", "expect", "consumer", "slot"},
    "acknowledge": {"op", "expect", "consumer", "slot", "drained"},
    "invalidate": {"op", "expect", "consumer", "slot"},
    "advance": {"op", "expect", "seconds"},
    "provider": {"op", "expect", "category", "count"},
}


def closed(value: Any, fields: set[str]) -> dict[str, Any]:
    """Refuse unknown fields, including credential or provider-URL material, before any rehearsal starts."""
    if not isinstance(value, dict) or set(value) != fields:
        raise Rejected("closed secret-free rehearsal object required")
    return value


def code(value: Any) -> str:
    """Accept only a bounded nonidentifying application/slot code, never free-form credentials or labels."""
    if (
        not isinstance(value, str)
        or re.fullmatch(r"[a-z][a-z0-9-]{0,31}", value) is None
    ):
        raise Rejected("bounded rehearsal code required")
    return value


def validate(data: Any) -> tuple[Policy, int]:
    """Fully validate closed policy and event shapes before replay; no mutation or partial history is published."""
    closed(data, {"schema", "consumers", "lease_ttl", "policy", "events"})
    if type(data["schema"]) is not int or data["schema"] != 1:
        raise Rejected("rehearsal schema 1 required")
    consumers = data["consumers"]
    if not isinstance(consumers, list) or not 1 <= len(consumers) <= 32:
        raise Rejected("one to 32 declared consumers required")
    for consumer in consumers:
        code(consumer)
    if len(set(consumers)) != len(consumers):
        raise Rejected("duplicate consumer")
    ttl = data["lease_ttl"]
    if type(ttl) is not int or not 3 <= ttl <= 3600:
        raise Rejected("fictional TTL must be 3..3600")
    policy = Policy(**closed(data["policy"], POLICY_KEYS))
    events = data["events"]
    if not isinstance(events, list) or not 1 <= len(events) <= 128:
        raise Rejected("one to 128 bounded events required")
    seconds, requested = 0.0, set()
    for event in events:
        if (
            not isinstance(event, dict)
            or not isinstance(event.get("op"), str)
            or event["op"] not in EVENT_KEYS
        ):
            raise Rejected("unknown rehearsal event")
        closed(event, EVENT_KEYS[event["op"]])
        if event["expect"] not in ("ok", "rejected", "unavailable"):
            raise Rejected("unknown expected outcome")
        if "consumer" in event:
            code(event["consumer"])
            code(event["slot"])
        if event["op"] == "request":
            if event["slot"] in requested:
                raise Rejected("request slot cannot be overwritten")
            requested.add(event["slot"])
        if event["op"] == "acknowledge" and type(event["drained"]) is not bool:
            raise Rejected("explicit boolean drain assertion required")
        if event["op"] == "advance":
            seconds += number(event["seconds"], 0, 3600)
            if seconds > 86400:
                raise Rejected("virtual timeline exceeds one-day bound")
        if event["op"] == "provider":
            if (
                event["category"]
                not in ("none", "unavailable", "denied", "invalid", "tls")
                or type(event["count"]) is not int
            ):
                raise Rejected("safe provider error/count required")
            if not (
                event["count"] == 0
                if event["category"] == "none"
                else 1 <= event["count"] <= 3
            ):
                raise Rejected("provider error count outside bound")
    return policy, ttl


class FictionalProvider(Scripted):
    """Keep original scripted error handling and fictional credential creation; change only the explicit TTL."""

    def __init__(self, clock: Clock, ttl: int):
        """Retain the original virtual clock/provider counters without real credentials or transport."""
        super().__init__(clock)
        self.ttl = ttl

    def issue(self) -> Lease:
        """Return an actual validated original Lease; no secret object crosses the public result boundary."""
        return replace(super().issue(), ttl=self.ttl)


def scenario(name: str) -> dict[str, str]:
    """Populate the same normal editable replay controls; selection alone does not execute events."""
    if name not in SCENARIOS:
        raise Rejected("unknown prepared rehearsal")
    return {
        "mode": MODES[1],
        **dict.fromkeys((name for name, _label, _kind in FIELDS), ""),
        "exercise": CHOICES["exercise"][SCENARIOS.index(name)],
    }


def acknowledgements(suffix: str) -> list[dict[str, Any]]:
    """Prepare ordinary request/exact-reference/drain events, not an automatic core acknowledgement bypass."""
    return [
        event
        for consumer in ("api-reader", "batch-reader", "report-reader")
        for event in (
            {
                "op": "request",
                "consumer": consumer,
                "slot": consumer + suffix,
                "expect": "ok",
            },
            {
                "op": "acknowledge",
                "consumer": consumer,
                "slot": consumer + suffix,
                "drained": True,
                "expect": "ok",
            },
        )
    ]


def prepared(name: str) -> dict[str, Any]:
    """Construct finite realistic handoff/outage scripts with literal expected safe categories."""
    if name not in CHOICES["exercise"]:
        raise Rejected("unknown handoff exercise")
    events: list[dict[str, Any]] = [
        {"op": "refresh", "expect": "ok"},
        *acknowledgements("-initial"),
    ]
    if name not in ("initial-handoff", "wrong-oracle", "undrained-ack"):
        events += [
            {"op": "advance", "seconds": 6, "expect": "ok"},
            {"op": "refresh", "expect": "ok"},
            {
                "op": "request",
                "consumer": "api-reader",
                "slot": "api-current",
                "expect": "ok",
            },
            {
                "op": "acknowledge",
                "consumer": "api-reader",
                "slot": "api-current",
                "drained": True,
                "expect": "ok",
            },
        ]
    if name in ("outage-grace", "outage-expired", "recovered"):
        events += [
            {
                "op": "advance",
                "seconds": 1 if name == "outage-grace" else 10,
                "expect": "ok",
            },
            {"op": "provider", "category": "unavailable", "count": 2, "expect": "ok"},
            {
                "op": "refresh",
                "expect": "ok" if name == "outage-grace" else "unavailable",
            },
        ]
        if name == "recovered":
            events += [
                {"op": "refresh", "expect": "ok"},
                *acknowledgements("-recovered"),
            ]
    elif name == "denied":
        events += [
            {"op": "provider", "category": "denied", "count": 1, "expect": "ok"},
            {"op": "refresh", "expect": "unavailable"},
        ]
    elif name == "stale-ack":
        events += [
            {
                "op": "acknowledge",
                "consumer": "batch-reader",
                "slot": "batch-reader-initial",
                "drained": True,
                "expect": "rejected",
            }
        ]
    elif name == "undrained-ack":
        # A fresh reference is requested; a false drain flag still cannot acknowledge it.
        events += [
            {"op": "advance", "seconds": 6, "expect": "ok"},
            {"op": "refresh", "expect": "ok"},
            {
                "op": "request",
                "consumer": "api-reader",
                "slot": "api-undrained",
                "expect": "ok",
            },
            {
                "op": "acknowledge",
                "consumer": "api-reader",
                "slot": "api-undrained",
                "drained": False,
                "expect": "rejected",
            },
        ]
    elif name == "late-old-failure":
        events += [
            {
                "op": "invalidate",
                "consumer": "api-reader",
                "slot": "api-reader-initial",
                "expect": "ok",
            },
            *[
                event
                for event in acknowledgements("-new")
                if event["consumer"] != "api-reader"
            ],
        ]
    elif name == "wrong-oracle":
        events[-1]["expect"] = "unavailable"
    return {
        "schema": 1,
        "consumers": ["api-reader", "batch-reader", "report-reader"],
        "lease_ttl": 10,
        "policy": asdict(Policy()),
        "events": events,
    }


def replay(data: dict[str, Any]) -> dict[str, Any]:
    """Drive the real core with controlled virtual time and actual in-memory lease reference binding."""
    policy, ttl = validate(data)
    clock = Clock()
    provider = FictionalProvider(clock, ttl)
    broker = Broker(provider, policy, clock=clock, sleep=clock.sleep)
    coordinator = Coordinator(broker, tuple(data["consumers"]))
    refs: dict[str, tuple[int, Lease]] = {}
    timeline = []
    for index, event in enumerate(data["events"], 1):
        observed = "ok"
        try:
            op = event["op"]
            if op == "advance":
                clock.sleep(float(event["seconds"]))
            elif op == "provider":
                provider.errors = (
                    []
                    if event["category"] == "none"
                    else [
                        ProviderError(
                            event["category"], event["category"] == "unavailable"
                        )
                        for _ in range(event["count"])
                    ]
                )
            elif op == "refresh":
                coordinator.refresh()
            elif op == "request":
                refs[event["slot"]] = coordinator.request(event["consumer"])
            else:
                if event["slot"] not in refs:
                    raise ValueError("no successful request for reference")
                generation, lease = refs[event["slot"]]
                if op == "acknowledge":
                    coordinator.acknowledge(
                        event["consumer"],
                        generation,
                        lease,
                        old_connections_drained=event["drained"],
                    )
                else:
                    coordinator.invalidate(event["consumer"], lease)
        except Unavailable:
            observed = "unavailable"
        except ValueError:
            observed = "rejected"
        timeline.append(
            {
                "index": index,
                "op": event["op"],
                "consumer": event.get("consumer"),
                "expected": event["expect"],
                "observed": observed,
                "expectation_met": observed == event["expect"],
                "virtual_seconds": clock(),
                "status": coordinator.status(),
                "broker_counters": broker.stats(),
            }
        )
    final = coordinator.status()
    return {
        "schema": 1,
        "mode": "virtual_original_core_handoff_rehearsal",
        "events": len(timeline),
        "matching_expectations": sum(row["expectation_met"] for row in timeline),
        "mismatches": sum(not row["expectation_met"] for row in timeline),
        "timeline": timeline,
        "final": final,
        "pending_consumers": [
            row for row in final["consumers"] if not row["current_acknowledged"]
        ],
        "broker_counters": broker.stats(),
        "fictional_provider_calls": provider.count,
        "scope": "Virtual original Broker/Coordinator only. Expected rejection is not authentication. Consumer/drain/timing assertions do not prove live pool termination, database acceptance or TLS. Forced refresh rehearsal does not measure automatic cache scheduling or concurrency. No credentials exported.",
    }


def analyze(
    state: Workspace, parameters: dict[str, str], stage: Path
) -> tuple[str, str, dict[str, bytes]]:
    """Validate original script, apply explicit finite effective policy, then save secret-free actual status only."""
    mode = parameters.get("mode")
    if mode not in MODES:
        raise Rejected("choose a supported offline handoff operation")
    raw = (
        read_source(Path(parameters.get("script", "")), 128 * 1024)
        if mode == MODES[0]
        else canonical(prepared(parameters.get("exercise", "")))
    )
    data = json_value(raw)
    original_policy, original_ttl = validate(data)
    data = copy.deepcopy(data)
    for name in ("expiry_guard", "base_delay", "max_delay"):
        if parameters.get(name):
            text = parameters[name]
            if (
                not text.isascii()
                or re.fullmatch(r"[0-9]{1,5}(?:\.[0-9]{1,6})?", text) is None
            ):
                raise Rejected("finite unsigned decimal policy control required")
            data["policy"][name] = float(text)
    for name in ("attempts", "lease_ttl"):
        if parameters.get(name):
            text = parameters[name]
            if not text.isascii() or not text.isdecimal() or len(text) > 4:
                raise Rejected("bounded integer policy control required")
            if name == "attempts":
                data["policy"][name] = int(text)
            else:
                data[name] = int(text)
    effective_policy, effective_ttl = validate(data)
    result = replay(data)
    scope = {
        "schema": 1,
        "input_sha256": hashlib.sha256(raw).hexdigest(),
        "effective_script_sha256": hashlib.sha256(canonical(data)).hexdigest(),
        "original_policy": asdict(original_policy),
        "effective_policy": asdict(effective_policy),
        "original_lease_ttl": original_ttl,
        "effective_lease_ttl": effective_ttl,
        "prepared_synthetic": mode == MODES[1],
        "real_provider_accessed": False,
        "real_database_accessed": False,
        "real_credentials_accepted": False,
        "credentials_exported": False,
        "scope": result["scope"],
    }
    return (
        "virtual-rotation-handoff",
        f"{result['matching_expectations']}/{result['events']} expected outcomes; {len(result['pending_consumers'])} consumers pending; virtual rehearsal only",
        {
            "handoff-rehearsal.json": canonical(result),
            "input-scope.json": canonical(scope),
        },
    )


def views(files: dict[str, bytes]) -> dict[str, list[dict[str, Any]]]:
    """Keep all outcomes/denominators and final pending-consumer status available independently of display filters."""
    r = json_value(files["handoff-rehearsal.json"])
    return {
        "Every actual core event outcome": [
            {"kind": "event", **row} for row in r["timeline"]
        ],
        "Final consumer handoff": [
            {"kind": "consumer", "current_generation": r["final"]["generation"], **row}
            for row in r["final"]["consumers"]
        ],
        "Pending consumers": [
            {"kind": "consumer", "current_generation": r["final"]["generation"], **row}
            for row in r["pending_consumers"]
        ],
        "Complete original core summary": [{"kind": "summary", **r}],
        "Original and effective policy scope": [
            {"kind": "scope", **json_value(files["input-scope.json"])}
        ],
    }


def cells(row: dict[str, Any]) -> tuple[str, str, str, str]:
    """Present actual event/generation values; no credential, lease identifier or secret repr is formatted."""
    if row["kind"] == "event":
        return (
            f"{row['index']}: {row['op']}"
            + (" / " + row["consumer"] if row["consumer"] else ""),
            row["expected"],
            row["observed"],
            "EXPECTED OUTCOME" if row["expectation_met"] else "MISMATCH",
        )
    if row["kind"] == "consumer":
        return (
            row["consumer"],
            f"Current {row['current_generation']}; requested {row['requested_generation']}",
            "Acknowledged " + str(row["acknowledged_generation"]),
            "CURRENT ASSERTION" if row["current_acknowledged"] else "NEEDS HANDOFF",
        )
    if row["kind"] == "summary":
        return (
            "Original-core virtual result",
            f"{row['matching_expectations']}/{row['events']} expected",
            str(row["mismatches"]) + " mismatches",
            str(len(row["pending_consumers"])) + " pending",
        )
    return (
        "Original / effective policy",
        str(row["original_policy"]),
        str(row["effective_policy"]),
        "No live provider/pool proof",
    )
