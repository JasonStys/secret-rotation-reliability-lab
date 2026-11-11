"""Independent original-core handoff outcomes, secret-free schema and explicit policy-change regressions. Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# definition: run — line 64
# parameter: changes — line 64
# parameter: name — line 64
# parameter: tmp_path — line 64
# variable: params — line 66
# definition: test_real_handoff_oracles — line 85
# parameter: events — line 85
# parameter: generation — line 85
# parameter: mismatches — line 85
# parameter: name — line 85
# parameter: pending — line 85
# parameter: tmp_path — line 85
# variable: files — line 87
# variable: r — line 88
# variable: rows — line 111
# variable: row — line 113
# variable: row — line 114
# variable: row — line 115
# variable: text — line 116
# variable: rows — line 122
# variable: row — line 123
# definition: test_actual_input_and_changed_ttl_keep_original — line 127
# parameter: tmp_path — line 127
# variable: source — line 129
# variable: raw — line 130
# variable: _ — line 132
# variable: files — line 132
# variable: r — line 145
# variable: s — line 145
# definition: test_unknown_consumer_missing_ref_replay_and_clear_provider — line 163
# variable: data — line 165
# variable: r — line 192
# variable: row — line 194
# definition: test_closed_script_negative_cases — line 257
# parameter: changes — line 257
# variable: data — line 259
# definition: test_event_count_time_budget_and_duplicate_slot — line 264
# variable: data — line 266
# variable: data — line 273
# definition: test_effective_controls_refuse_invalid_values — line 299
# parameter: key — line 299
# parameter: tmp_path — line 299
# parameter: value — line 299
# definition: test_original_policy_is_not_repaired_silently — line 305
# parameter: tmp_path — line 305
# variable: data — line 307
# variable: source — line 309
# variable: data — line 315
# definition: test_unknown_mode_and_examples — line 320
# parameter: tmp_path — line 320
# variable: call — line 322
# END CODE MAP

import copy

import pytest

from rotation import desktop_project as p
from rotation.desktop_io import canonical, json_value


def run(tmp_path, name, **changes):
    """Exercise the exact project adapter used by real native controls with explicitly synthetic data."""
    params = p.scenario(p.SCENARIOS[p.CHOICES["exercise"].index(name)]) | changes
    return p.analyze(None, params, tmp_path)[2]


@pytest.mark.parametrize(
    "name,generation,pending,events,mismatches",
    [
        ("initial-handoff", 1, 0, 7, 0),
        ("partial-rotation", 2, 2, 11, 0),
        ("outage-grace", 2, 2, 14, 0),
        ("outage-expired", 2, 3, 14, 0),
        ("recovered", 3, 0, 21, 0),
        ("denied", 2, 3, 13, 0),
        ("stale-ack", 2, 2, 12, 0),
        ("undrained-ack", 2, 3, 11, 0),
        ("late-old-failure", 2, 0, 16, 0),
        ("wrong-oracle", 1, 0, 7, 1),
    ],
)
def test_real_handoff_oracles(tmp_path, name, generation, pending, events, mismatches):
    """Generation, consumer backlog and mismatches are independently specified, never inferred from a green label."""
    files = run(tmp_path, name)
    r = json_value(files["handoff-rehearsal.json"])
    assert (
        r["final"]["generation"],
        len(r["pending_consumers"]),
        r["events"],
        r["mismatches"],
    ) == (generation, pending, events, mismatches)
    assert r["matching_expectations"] + r["mismatches"] == events
    assert r["final"]["all_consumers_acknowledged"] is (pending == 0)
    if name in ("stale-ack", "undrained-ack"):
        assert r["timeline"][-1]["observed"] == "rejected"
    if name == "outage-grace":
        assert r["broker_counters"]["fallbacks"] == 1
        assert r["final"]["previous_overlap_usable"] is True
    if name == "outage-expired":
        assert r["timeline"][-1]["observed"] == "unavailable"
        assert r["final"]["current_lease_usable"] is False
    if name == "denied":
        assert (
            r["broker_counters"]["denials"] == 1
            and r["broker_counters"]["fallbacks"] == 0
        )
    if name == "partial-rotation":
        rows = p.views(files)["Pending consumers"]
        assert len(rows) == 2
        assert all(row["current_generation"] == 2 for row in rows)
        assert all("Current 2; requested 1" == p.cells(row)[1] for row in rows)
        assert all("Acknowledged 1" == p.cells(row)[2] for row in rows)
    text = b"".join(files.values()).decode()
    assert (
        "not-a-real-database-credential" not in text
        and "database/creds/reader/" not in text
        and "fictional-1" not in text
    )
    for rows in p.views(files).values():
        for row in rows:
            assert len(p.cells(row)) == 4


def test_actual_input_and_changed_ttl_keep_original(tmp_path):
    """A longer lease changes the expiry oracle visibly; original bytes/policy remain separately bound."""
    source = tmp_path / "authorized-script.json"
    raw = canonical(p.prepared("outage-expired"))
    source.write_bytes(raw)
    _, _, files = p.analyze(
        None,
        {
            "mode": p.MODES[0],
            "script": str(source),
            "lease_ttl": "20",
            "attempts": "2",
            "expiry_guard": "1.0",
            "base_delay": "0.05",
            "max_delay": "0.2",
        },
        tmp_path,
    )
    r, s = (
        json_value(files["handoff-rehearsal.json"]),
        json_value(files["input-scope.json"]),
    )
    assert r["mismatches"] == 1 and r["timeline"][-1]["observed"] == "ok"
    assert s["original_lease_ttl"] == 10 and s["effective_lease_ttl"] == 20
    assert (
        s["input_sha256"] != s["effective_script_sha256"] and source.read_bytes() == raw
    )
    assert (
        s["real_provider_accessed"]
        is s["real_database_accessed"]
        is s["real_credentials_accepted"]
        is s["credentials_exported"]
        is False
    )


def test_unknown_consumer_missing_ref_replay_and_clear_provider():
    """Actual core refusals are visible events; a nonexistent request cannot manufacture a valid acknowledgement."""
    data = p.prepared("initial-handoff")
    data["events"] += [
        {
            "op": "request",
            "consumer": "unknown",
            "slot": "missing",
            "expect": "rejected",
        },
        {
            "op": "acknowledge",
            "consumer": "api-reader",
            "slot": "missing",
            "drained": True,
            "expect": "rejected",
        },
        {
            "op": "acknowledge",
            "consumer": "api-reader",
            "slot": "api-reader-initial",
            "drained": True,
            "expect": "rejected",
        },
        {"op": "provider", "category": "tls", "count": 1, "expect": "ok"},
        {"op": "refresh", "expect": "unavailable"},
        {"op": "provider", "category": "none", "count": 0, "expect": "ok"},
        {"op": "refresh", "expect": "ok"},
    ]
    r = p.replay(data)
    assert r["mismatches"] == 0 and r["final"]["generation"] == 2
    assert [row["observed"] for row in r["timeline"][-7:-4]] == ["rejected"] * 3
    assert len(r["pending_consumers"]) == 3


@pytest.mark.parametrize(
    "changes",
    [
        {"schema": True},
        {"schema": 2},
        {"consumers": []},
        {"consumers": ["x", "x"]},
        {"consumers": ["unsafe identifier"]},
        {"lease_ttl": True},
        {"lease_ttl": 2},
        {"events": []},
        {"events": [{"op": "shell", "expect": "ok"}]},
        {"events": [{"op": "refresh", "expect": "ok", "password": "inert-rejected"}]},
        {"events": [{"op": "refresh", "expect": "success"}]},
        {
            "events": [
                {
                    "op": "acknowledge",
                    "consumer": "api",
                    "slot": "a",
                    "drained": 1,
                    "expect": "ok",
                }
            ]
        },
        {"events": [{"op": "advance", "seconds": float("inf"), "expect": "ok"}]},
        {"events": [{"op": "advance", "seconds": 3601, "expect": "ok"}]},
        {
            "events": [
                {"op": "provider", "category": "none", "count": 1, "expect": "ok"}
            ]
        },
        {
            "events": [
                {
                    "op": "provider",
                    "category": "unavailable",
                    "count": 4,
                    "expect": "ok",
                }
            ]
        },
        {
            "events": [
                {
                    "op": "provider",
                    "category": "raw-provider-error",
                    "count": 1,
                    "expect": "ok",
                }
            ]
        },
        {
            "events": [
                {"op": "provider", "category": "tls", "count": True, "expect": "ok"}
            ]
        },
    ],
)
def test_closed_script_negative_cases(changes):
    """Malformed/credential-bearing/oversized event controls fail before actual replay rather than being ignored."""
    data = p.prepared("initial-handoff") | copy.deepcopy(changes)
    with pytest.raises(ValueError):
        p.validate(data)


def test_event_count_time_budget_and_duplicate_slot():
    """Closed replay stays finite and cannot silently rebind a previously named request slot."""
    data = p.prepared("initial-handoff")
    data["events"] = [{"op": "refresh", "expect": "ok"}] * 129
    with pytest.raises(ValueError):
        p.validate(data)
    data["events"] = [{"op": "advance", "seconds": 3600, "expect": "ok"}] * 25
    with pytest.raises(ValueError):
        p.validate(data)
    data = p.prepared("initial-handoff")
    data["events"].append(
        {
            "op": "request",
            "consumer": "api-reader",
            "slot": "api-reader-initial",
            "expect": "ok",
        }
    )
    with pytest.raises(ValueError):
        p.validate(data)


@pytest.mark.parametrize(
    "key,value",
    [
        ("lease_ttl", "2"),
        ("lease_ttl", "99999"),
        ("attempts", "0"),
        ("attempts", "١"),
        ("expiry_guard", "NaN"),
        ("base_delay", "-1"),
        ("max_delay", "0.001"),
        ("expiry_guard", "31"),
    ],
)
def test_effective_controls_refuse_invalid_values(tmp_path, key, value):
    """Optional controls cannot bypass original Policy/Lease range and type boundaries."""
    with pytest.raises(ValueError):
        run(tmp_path, "initial-handoff", **{key: value})


def test_original_policy_is_not_repaired_silently(tmp_path):
    """An otherwise valid GUI override cannot hide invalid source settings or extra credentials."""
    data = p.prepared("initial-handoff")
    data["policy"]["attempts"] = False
    source = tmp_path / "bad.json"
    source.write_bytes(canonical(data))
    with pytest.raises(ValueError):
        p.analyze(
            None, {"mode": p.MODES[0], "script": str(source), "attempts": "2"}, tmp_path
        )
    data = p.prepared("initial-handoff") | {"token": "inert-rejected-fixture"}
    with pytest.raises(ValueError):
        p.validate(data)


def test_unknown_mode_and_examples(tmp_path):
    """No hidden live-provider operation or unknown prepared input is executable."""
    for call in (
        lambda: p.scenario("unknown"),
        lambda: p.prepared("unknown"),
        lambda: p.analyze(None, {"mode": "rotate-production"}, tmp_path),
    ):
        with pytest.raises(ValueError):
            call()
