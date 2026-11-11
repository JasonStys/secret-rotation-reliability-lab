# Secret Rotation Rehearsal Workbench: native application

Created by **Jason Stys** · [Source/contact](https://github.com/JasonStys) · [Professional profile](https://www.linkedin.com/in/jason-stys-31b30b351/).

Replay authorized closed secret-free event scripts through the actual Broker, Policy, Lease and Coordinator. Inspect requested versus current generations, expiry windows, rejected stale/undrained acknowledgements, outage grace/expiry, recovery and wrong expected outcomes. The provider is explicitly fictional; no real credential or service is requested.

## Launch and practical controls

The Windows x64 portable candidate is `SecretRotationReliabilityLab.exe`. Its complete real Tk interface and original project engines bundle CPython 3.14.10, Tcl/Tk 9.0.4 and actual original runtime notices. A reviewed download needs no separately installed Python, Node, command setup, default password or background service. It is a portable EXE, not an NSIS installer, Authenticode-signed product or a claim that a public distribution already exists. Publication/download availability is a separate reviewed gate.

1. Select **Replay authorized secret-free handoff script**, choose your JSON file and run through normal authorized-input controls. The closed document contains `schema: 1`, one to 32 unique application consumer codes, `lease_ttl`, a complete original `policy` and one to 128 events. Do not put identifying or secret values in codes, file names or paths; syntax validation is not a universal secret detector.
2. Each event declares `expect` as `ok`, `rejected` or `unavailable`. Operations are `refresh`; `request` with consumer/slot; `acknowledge` with consumer/slot/boolean `drained`; `invalidate` with consumer/slot; `advance` with finite seconds; and `provider` with one safe category/count. Slot references bind actual in-memory requested objects/generations; no caller-supplied lease ID, password or generation can bypass the original coordinator.
3. Optional guard, retry-delay, attempt and fictional-TTL controls change only effective policy. Original policy is validated first and both sets/hashes remain visible. All advance/retry time is virtual and never changes the system clock or sleeps through a real outage. Refresh events are intentionally forced handoff refreshes; they do not measure automatic cached-get scheduling or concurrency.
4. Ten prepared cases run inside the same application: initial/partial handoff, usable-cache outage, expired outage, recovery, denied refresh, stale acknowledgement, undrained acknowledgement, late old-object failure, and an intentionally wrong expected outcome. The wrong oracle remains a visible mismatch; a matching expected rejection is not successful authentication.
5. Inspect every event, final consumer state, pending queue, broker counters and original/effective policy. The table displays current generation alongside requested/acknowledged generations, so equal old numbers cannot imply a current handoff. Search/filter keeps full counts; exact export creates a new file; saved evidence persists across normal Exit/restart. Delete requires confirmation.

## Private local profile and completion

The default durable profile lives in the OS-local application-data directory under `SecretRotationReliabilityLab`, outside the executable and Git repository. An explicit `--profile` remains available for an authorized dedicated directory. Original CLI paths/contracts are preserved. Reports and chosen paths are sensitive owner-local plaintext: no encryption, multiuser login or hostile-administrator isolation is claimed.

Before SQLite initialization, all lexical ancestors and fixed marker, lock, database and journal/WAL/SHM files are checked for aliases, nonregular entries and multiple links. Ordinary owned recovery sidecars are retained; unknown/nonempty directories are not reset. The profile owner lock remains held through analysis, immutable evidence commit and actual worker completion. Busy Exit keeps its owner window/lock rather than force-killing a worker or silently abandoning a transaction. Static checks do not isolate a malicious same-user process replacing paths concurrently.

Supported inputs use bounded stable ordinary-descriptor reads, strict JSON and the original closed domain parsers. Unrecognized fields, duplicates, nonfinite values, unsafe bounds or invalid metadata are refused without reflecting raw inputs. Export is exact and refuses overwrite. Help and complete original Python/Tcl/Tk/freezer notices work offline. No HTTP listener, provider account, telemetry, popup-ad integration, arbitrary executable, script/plugin evaluator or background upload is introduced.

## Build and actual executable acceptance

Use a dedicated environment with the reviewed Windows CPython 3.14.10 runtime:

```text
python -m pip install --require-hashes -r requirements-dev.lock -r requirements-native.lock
python -m pip check
python scripts/build_native.py
python scripts/test_native_app.py
```

The one-file build binds its exact source SHA, honest dirty flag, actual Python DLL, original notices and allowlisted resources. The consumer starts the real EXE with a minimal system-only environment and explicit synthetic profile, drives the same widgets/handlers/mainloop, uses actual file chooser paths, checks independent domain oracles, captures two actual native screens, normally exits and repeats against the same durable history. CI rejects dirty source and verifies both owned bootloader/frozen PIDs are gone. No real user profile or installed application is opened.

The compiled consumer checks ten prepared scripts plus two actual selected scripts, including a longer TTL that visibly changes the expiry oracle. Independent hardcoded cases bind final generations, event counts, pending consumers and mismatches; exact-object stale failures cannot erase a new generation; stale/replayed/undrained acknowledgements remain rejected; outages stop at expiry; a wrong oracle remains one mismatch. Exact export, invalid-input retention, cancel/confirm deletion, licenses and twelve unchanged saved bundles across two normal launches are required.

The source-quality lanes independently require their actual selected Python to import both native `_tkinter` and `tkinter`, construct/query a no-display Tcl interpreter and validate loaded/compiled families. This is distinct from a graphical display test. There is no redundant distro-Python Tk install, ignored error, fallback or skip. The real compiled Windows journey remains the graphical proof.

## Limits and original tools

This is virtual in-process behavior of the original core, not live OpenBao/TLS/PostgreSQL, database-pool termination, provider authentication, production availability, concurrency measurement or a password vault. Consumer/drain flags remain assertions. No real provider URL, token, password, arbitrary program or live action is accepted. Original broker concurrency/property tests and actual isolated TLS/Go-module/database lifecycle gates remain intact and mandatory.

[Dated candidate validation](reports/native-workbench-2026-11-11.md). Existing Office guides and historical reports keep their own recorded source identities; they are not relabeled as current native release/install proof.

## Minimal custom replay file

This deliberately incomplete one-consumer handoff should leave a pending consumer; a refresh alone is not acknowledgement. All fields are inert schema data.

```json
{"schema":1,"consumers":["api-reader"],"lease_ttl":10,"policy":{"refresh_fraction":0.6,"expiry_guard":1.0,"attempts":2,"base_delay":0.05,"max_delay":0.2},"events":[{"op":"refresh","expect":"ok"},{"op":"request","consumer":"api-reader","slot":"initial","expect":"ok"}]}
```

To acknowledge, add a separate `acknowledge` event with the same consumer/slot, explicit boolean `drained` and `expect`. A true drain flag is still a supplied in-process assertion, not proof that a real connection pool was terminated.
