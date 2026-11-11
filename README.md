# Secret Rotation Reliability Lab

[![Validate](https://github.com/JasonStys/secret-rotation-reliability-lab/actions/workflows/ci.yml/badge.svg)](https://github.com/JasonStys/secret-rotation-reliability-lab/actions/workflows/ci.yml)
[![CodeQL](https://github.com/JasonStys/secret-rotation-reliability-lab/actions/workflows/codeql.yml/badge.svg)](https://github.com/JasonStys/secret-rotation-reliability-lab/actions/workflows/codeql.yml)

Created by **Jason Stys** · [GitHub](https://github.com/JasonStys) · [LinkedIn](https://www.linkedin.com/in/jason-stys-31b30b351/)

A defensive DevOps lab that tests what happens **after a database password changes**: credential handoff, lease expiry, identity revocation and a secrets-manager outage. It uses a real OpenBao PostgreSQL secrets engine rather than inventing a password vault. Native deterministic/property/concurrency tests and a completely separate live TLS exercise distinguish a convincing demo from evidence.

This is an isolated learning/portfolio project, **not a production secrets service, military compliance certification, zero-downtime guarantee or authorization to touch someone else's infrastructure**. All data and credentials are fictional/disposable. The live drill refuses Windows/macOS and requires explicit acknowledgement on a disposable Linux Docker host. Local Docker Desktop is left unchanged.

The reviewed CI manager is a **lab-maintained OpenBao rebuild** with an explicitly unsupported Okta login-MFA integration. That unused integration always returns an error; it cannot silently bypass MFA or authenticate. A hash-bound source patch removes the obsolete Okta SDK's vulnerable jose/v3 linkage, with an actual upstream-package fail-closed test before the unchanged binary scan and database lifecycle drill. Other authentication and PostgreSQL secret-engine paths retain their genuine upstream implementation. See [build scope and security correction](docs/upstream-security.md); this is not an upstream-signed full-feature release.

## Native offline workbench

**Secret Rotation Rehearsal Workbench 1.1.0** adds real native authorized-file/configuration controls, original-engine outcomes, complete evidence, literal search/filter, exact export and durable history. Prepared cases are inputs inside the same full app. [Usage, schemas, profile/privacy and complete compiled test](docs/native-application.md) · [Dated candidate evidence](docs/reports/native-workbench-2026-11-11.md).

Replay authorized closed secret-free event scripts through the actual Broker, Policy, Lease and Coordinator. Inspect requested versus current generations, expiry windows, rejected stale/undrained acknowledgements, outage grace/expiry, recovery and wrong expected outcomes. The provider is explicitly fictional; no real credential or service is requested. The portable Windows recipe bundles the patched runtime; actual publication and PC installation are separate review steps, not inferred from a source badge.

## Features and major functions

| Component | What it demonstrates |
| --- | --- |
| `Lease` / `Policy` | Printable bounded credentials, strict int/bool rules, finite settings, conservative monotonic deadlines and early refresh. |
| `Broker.get` | One refresh for concurrent callers, finite capped retry, transient-only valid-cache fallback and strict expiry rejection. TLS/authorization/malformed-provider failures invalidate the cache immediately. |
| `Broker.invalidate` | A late failure on an old lease cannot erase a newer generation. Consumers must close/drain their old database connections. |
| [Multi-consumer handoff](docs/consumer-handoff.md) | Exact requested generation/object acknowledgement, per-consumer drain assertions, stale/replay rejection, overlap/outage/expiry work queues and a separate finite virtual-time demo. Broker refresh never implies every consumer switched. |
| `Transport` / `BaoProvider.issue` | Verified TLS1.2+, numeric loopback-only URLs, no proxies/redirects, bounded JSON, duplicate-key rejection and safe error categories. |
| Live drill | Real SCRAM/verify-full database connections, exact read-only permissions, overlapping identities, operator renewal, individual/TTL/token revocation, dedicated manager-password rotation, stopped-manager grace/expiry/recovery and HMAC audit verification. |
| Evidence | Exact allowlisted aggregates and inert HTML; no passwords, tokens, lease IDs, raw logs or arbitrary provider messages can enter a report. |
| CI | Four native OS/Python lanes, real Linux services, source-bound scanned PostgreSQL image, actual OpenBao Go-module audit, dependency/secrets/workflow/CodeQL gates; **no Actions artifacts/caches**. |

## Quick start — no Docker required

Python 3.12+ and Git are required. From a clone, create a virtual environment and install the hash-locked development tools:

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install --require-hashes -r requirements-dev.lock
.venv\Scripts\python.exe -m rotation demo --output out/my-first-demo
.venv\Scripts\python.exe -m rotation report out/my-first-demo/report.json
.venv\Scripts\python.exe -m pytest --cov
```

On Linux/macOS replace `.venv\Scripts\python.exe` with `.venv/bin/python`. Open `out/my-first-demo/report.html` as a local file. This eight-case offline demonstration is **simulation**, not proof that a live manager/database was contacted. Outputs must be new directories; no report is overwritten. See [runbook](docs/runbook.md) for the live drill and troubleshooting.

## Architecture and deliberate boundaries

```text
consumer → single-flight Broker → verified TLS OpenBao → leased PostgreSQL reader
              │                        │
        expiry/identity guard     HMAC audit (private)
              └──────── allowlisted counters/cases → inert report
```

Python provides portable typed orchestration and tests; OpenBao's native Go implementation handles credential generation/leases; PostgreSQL/SQL enforces data privileges; HCL makes authorization reviewable; Bash enforces CI fail-fast checks; HTML presents safe evidence. Languages are chosen for their actual role, not inserted as unused wrappers. Runtime `rotation/` has no third-party dependencies. Psycopg's native libpq is needed only by the CPython3.14/Linux-x86_64 live drill.

The app token can **only** issue `database/creds/reader` credentials. A dedicated non-superuser database manager creates/revokes these roles; its own original password is rotated away. The fixture PostgreSQL administrator is used by the isolated test oracle, never by application consumers. Manager bootstrap uses in-memory storage, one-share unseal and an ephemeral root token: these are explicitly lab-only tradeoffs. Host/Docker administrators can access local test material; this is not protection against the host administrator or guaranteed memory erasure.

Changing a password does not terminate an existing PostgreSQL session. The example always opens/closes scoped connections, proves new authentication and privileges, and verifies dropped roles separately. A production connection pool requires explicit drain/termination and workload-specific failure handling. See [ADR](docs/architecture.md), [contracts](docs/contracts.md), [threat model](docs/threat-model.md), [testing strategy](docs/testing.md) and [measured validation](docs/reports/validation.md).

## Repository organization

Shallow folders: `rotation/` (portable core/CLI), `scripts/` (owned drill and gates), `ops/` (HCL/startup), `sql/` (fictional data/privileges), `tests/`, `docs/`, `.github/workflows/`. Generated binaries, keys, environment files, raw audit logs and working data remain ignored under `.tools/` or `out/` and are never uploaded. Reports below are selected synthetic aggregates, not a secret/log archive.

Headers map definitions, parameters and assigned variables/attributes to exact lines. `python scripts/code_map.py --check` rejects stale maps/missing function/class contracts; regenerate after formatting. The tracked-file inventory below is mechanically checked in CI. Time complexity and coverage boundaries are documented, not guessed from timing.

<!-- BEGIN FILE GUIDE -->

| File | Purpose |
| --- | --- |
| [.dockerignore](.dockerignore) | Allow only Dockerfile and reviewed startup script into the image build. |
| [.gitattributes](.gitattributes) | Consistent LF source checkout across operating systems. |
| [.github/workflows/ci.yml](.github/workflows/ci.yml) | Jason Stys: portable credential tests, real TLS OpenBao/PostgreSQL lifecycle and security; zero artifacts/caches. |
| [.github/workflows/codeql.yml](.github/workflows/codeql.yml) | Jason Stys: security-extended Python analysis with scoped upload permissions and no database archive upload. |
| [.gitignore](.gitignore) | Keep generated keys, credentials, logs, tools and working data untracked. |
| [CONTRIBUTING.md](CONTRIBUTING.md) | Contributing and maintenance. |
| [Dockerfile](Dockerfile) | Jason Stys: derived non-root-only PostgreSQL lab image; remove unused vulnerable root-switch helper. |
| [LICENSE](LICENSE) | MIT terms for authored source; upstream tools retain their licenses. |
| [README.md](README.md) | Secret Rotation Reliability Lab. |
| [SECURITY.md](SECURITY.md) | Security policy. |
| [docs/architecture.md](docs/architecture.md) | ADR-001: delegated secrets management with a conservative consumer. |
| [docs/consumer-handoff.md](docs/consumer-handoff.md) | Multi-consumer generation handoff. |
| [docs/contracts.md](docs/contracts.md) | Lifecycle, data and privacy contracts. |
| [docs/handbook.md](docs/handbook.md) | Secret Rotation Reliability Lab handbook. |
| [docs/native-application.md](docs/native-application.md) | Secret Rotation Rehearsal Workbench: native application. |
| [docs/reports/benchmark.json](docs/reports/benchmark.json) | Actual warmed broker benchmark with a one-issuance oracle. |
| [docs/reports/ci.json](docs/reports/ci.json) | Immutable executable-source acceptance snapshot with actual completed checks. |
| [docs/reports/documentation-refresh-2026-11-09.md](docs/reports/documentation-refresh-2026-11-09.md) | Documentation refresh — 2026-11-09. |
| [docs/reports/handoff-2026-11-09.md](docs/reports/handoff-2026-11-09.md) | Multi-consumer handoff validation — 2026-11-09. |
| [docs/reports/image-library-security-2026-11-11.md](docs/reports/image-library-security-2026-11-11.md) | Actual derived-image library security repair — 2026-11-11. |
| [docs/reports/installed-windows-1.1.0-r2-2026-11-11.md](docs/reports/installed-windows-1.1.0-r2-2026-11-11.md) | Observed installed workflows, delivery evidence, data preservation and practical limits. |
| [docs/reports/live.html](docs/reports/live.html) | Inert HTML rendering of the selected actual service aggregate. |
| [docs/reports/live.json](docs/reports/live.json) | Selected actual service case durations and safe lifecycle counters. |
| [docs/reports/native-workbench-2026-11-11.md](docs/reports/native-workbench-2026-11-11.md) | Native offline workbench validation — 2026-11-11. |
| [docs/reports/portfolio-sync-2026-10-22.md](docs/reports/portfolio-sync-2026-10-22.md) | <!-- File: docs/reports/portfolio-sync-2026-10-22.md; Purpose: certificate-bundle security repair and evidence by Jason Stys. -->. |
| [docs/reports/project-guide.docx](docs/reports/project-guide.docx) | Reviewed Word project guide bound to the documented source revision. |
| [docs/reports/publications.json](docs/reports/publications.json) | Exact Office digests, visual review scopes and immutable source baselines. |
| [docs/reports/security-repair-2026-11-09.md](docs/reports/security-repair-2026-11-09.md) | Maintained dependency repair validation — November 9, 2026. |
| [docs/reports/simulation.html](docs/reports/simulation.html) | Inert HTML rendering of the clearly labeled offline simulation. |
| [docs/reports/simulation.json](docs/reports/simulation.json) | Explicitly simulated offline assertions and virtual elapsed times. |
| [docs/reports/validation.md](docs/reports/validation.md) | Measured validation and author review. |
| [docs/reports/windows-application-guide-1.1.0-r2.docx](docs/reports/windows-application-guide-1.1.0-r2.docx) | Current peer-reviewed installed app guide with actual screenshots and immutable code. |
| [docs/reports/windows-application-guide-1.1.0-r2.json](docs/reports/windows-application-guide-1.1.0-r2.json) | Exact guide, source, image and individually reviewed page identities. |
| [docs/research.md](docs/research.md) | Primary-source research and implementation choices. |
| [docs/runbook.md](docs/runbook.md) | Runbook: safe local demonstration and owned live exercise. |
| [docs/testing.md](docs/testing.md) | Test strategy and reproducible validation. |
| [docs/threat-model.md](docs/threat-model.md) | Threat model and deployment limits. |
| [docs/upstream-security.md](docs/upstream-security.md) | Reviewed upstream security rebuild. |
| [ops/reader.hcl](ops/reader.hcl) | Jason Stys: application token can issue ONLY reader credentials; everything else remains default-deny. |
| [ops/start-postgres.sh](ops/start-postgres.sh) | Jason Stys: bounded wait for owned, generated TLS fixture files, then exec the native PostgreSQL entrypoint. |
| [patches/disable-unused-okta-mfa.patch](patches/disable-unused-okta-mfa.patch) | Reviewed hash-bound upstream lab patch: unsupported Okta login MFA always rejects, removing obsolete SDK linkage; actual Go regression included. |
| [pyproject.toml](pyproject.toml) | Strict lint/type/test/statement-and-branch coverage configuration. |
| [requirements-dev.in](requirements-dev.in) | Exact portable development tool inputs. |
| [requirements-dev.lock](requirements-dev.lock) | Complete hash-locked portable development graph. |
| [requirements-integration.in](requirements-integration.in) | Exact live-only PostgreSQL driver input. |
| [requirements-integration.lock](requirements-integration.lock) | Hash-locked CPython3.14/Linux-x86_64 live-only driver graph. |
| [requirements-native.lock](requirements-native.lock) | Exact complete hash-locked native freezing tool graph; no runtime setup dependency. |
| [rotation/\_\_init\_\_.py](rotation/__init__.py) | Credential lifecycle contracts and safe evidence by Jason Stys; no import-time I/O. |
| [rotation/\_\_main\_\_.py](rotation/__main__.py) | Offline demo and strict aggregate inspection CLI; raw secrets/errors never printed. Created by Jason Stys. |
| [rotation/bao.py](rotation/bao.py) | Verified TLS, no redirects/proxies, bounded OpenBao JSON and safe provider errors. Created by Jason Stys. |
| [rotation/broker.py](rotation/broker.py) | Single-flight credential refresh with bounded retry, safe statistics and stale-lease guards. Jason Stys. |
| [rotation/contracts.py](rotation/contracts.py) | Bounded lease/policy contracts; secret fields never enter representations. Created by Jason Stys. |
| [rotation/desktop.py](rotation/desktop.py) | Native offline workbench: real project inputs, analysis, searchable evidence, history and export. Jason Stys. |
| [rotation/desktop\_io.py](rotation/desktop_io.py) | Bounded regular descriptor reads and strict finite JSON for owner-local desktop state. Jason Stys. |
| [rotation/desktop\_project.py](rotation/desktop_project.py) | Replay closed secret-free handoff scripts through the real Broker/Coordinator with virtual time. Jason Stys. |
| [rotation/desktop\_state.py](rotation/desktop_state.py) | Owner-local desktop profile, bounded durable bundles and non-overwriting export. Jason Stys. |
| [rotation/evidence.py](rotation/evidence.py) | Allowlisted aggregate reports, inert escaped HTML and new-directory-only output. Created by Jason Stys. |
| [rotation/handoff.py](rotation/handoff.py) | Generation-bound multi-consumer acknowledgements; credentials never enter status. Created by Jason Stys. |
| [rotation/inputs.py](rotation/inputs.py) | Bounded stable ordinary-file reads and streaming tool hashes for offline identity inputs. Jason Stys. |
| [rotation/simulation.py](rotation/simulation.py) | Deterministic offline lifecycle demonstration, explicitly NOT live-manager evidence. Created by Jason Stys. |
| [scripts/\_\_init\_\_.py](scripts/__init__.py) | Opt-in disposable exercise and maintained-repository helpers by Jason Stys; no import-time I/O. |
| [scripts/bao\_check.py](scripts/bao_check.py) | Scan the actual verified OpenBao binary's Go module inventory with no advisory exclusions. Created by Jason Stys. |
| [scripts/benchmark.py](scripts/benchmark.py) | Measure warmed cached broker decisions with an independent one-issuance oracle. Created by Jason Stys. |
| [scripts/build\_bao.py](scripts/build_bao.py) | Build pinned upstream OpenBao with reviewed maintained authentication/network dependencies, never suppressing advisories. Created by Jason Stys. |
| [scripts/build\_native.py](scripts/build_native.py) | Build the complete real offline workbench as one Windows portable executable. Jason Stys. |
| [scripts/check\_tk\_runtime.py](scripts/check_tk_runtime.py) | Require the selected interpreter's actual native Tk imports and loaded Tcl, without a display. Jason Stys. |
| [scripts/code\_map.py](scripts/code_map.py) | Generate/check exact Python, SQL, shell and YAML symbol positions. Created by Jason Stys. |
| [scripts/file\_guide.py](scripts/file_guide.py) | Maintain a complete tracked-file README purpose inventory; unknown file types fail closed. Created by Jason Stys. |
| [scripts/image\_check.py](scripts/image_check.py) | Build/scan a non-root-only image from the immutable official PostgreSQL base; do not suppress vulnerabilities. Jason Stys. |
| [scripts/live\_drill.py](scripts/live_drill.py) | Real TLS OpenBao/PostgreSQL lifecycle on an acknowledged disposable Linux Docker host. Created by Jason Stys. |
| [scripts/native\_acceptance.py](scripts/native_acceptance.py) | Actual final portable widgets/core/native-window acceptance with independent oracles. Jason Stys. |
| [scripts/native\_common.py](scripts/native_common.py) | Actual patched Python/Tcl/Tk/PyInstaller runtime notices and authored portable icon. Jason Stys. |
| [scripts/native\_entry.py](scripts/native_entry.py) | Launch the actual bundled offline project workbench; no setup shell commands. Jason Stys. |
| [scripts/scanners.py](scripts/scanners.py) | Install only hash-pinned official Linux scanner binaries. Created by Jason Stys. |
| [scripts/test\_native\_app.py](scripts/test_native_app.py) | Run the real frozen workbench twice with an owned synthetic profile and exact bundle persistence. Jason Stys. |
| [scripts/validate.sh](scripts/validate.sh) | Jason Stys: strict portable tests and maintained source/documentation contracts; no Actions storage uploads. |
| [scripts/validate\_repo.py](scripts/validate_repo.py) | Gate immutable pins, workflow permission/storage and credential tracking invariants. Created by Jason Stys. |
| [sql/seed.sql](sql/seed.sql) | Jason Stys: fictional product inventory and dedicated non-superuser credential manager privileges. |
| [tests/test\_bao.py](tests/test_bao.py) | Provider protocol and transport adversarial tests; fake sockets never access outside networks. Jason Stys. |
| [tests/test\_broker.py](tests/test_broker.py) | Deterministic retry/expiry/identity/race tests plus actual concurrent single-flight threads. Jason Stys. |
| [tests/test\_build\_diagnostics.py](tests/test_build_diagnostics.py) | Public Docker package failure diagnostics stay bounded and credential/terminal safe. Jason Stys. |
| [tests/test\_contracts.py](tests/test_contracts.py) | Independent lease/policy boundary and fuzz/property tests; all values fictional. Created by Jason Stys. |
| [tests/test\_desktop\_gui.py](tests/test_desktop_gui.py) | Presentation-adapter unit tests with real core/SQLite workers; real widgets are separately frozen-tested. Jason Stys. |
| [tests/test\_desktop\_io.py](tests/test_desktop_io.py) | Private state JSON and bounded descriptor-read boundary cases with actual file bytes. Jason Stys. |
| [tests/test\_desktop\_project.py](tests/test_desktop_project.py) | Independent original-core handoff outcomes, secret-free schema and explicit policy-change regressions. Jason Stys. |
| [tests/test\_desktop\_state.py](tests/test_desktop_state.py) | Independent offline desktop ownership, byte-bound, SQLite and non-overwrite regressions. Jason Stys. |
| [tests/test\_evidence.py](tests/test_evidence.py) | Strict evidence schema, output privacy, real CLI control flow and aggregate negative tests. Jason Stys. |
| [tests/test\_handoff.py](tests/test_handoff.py) | Real portable broker/coordinator consumer handoff, replay, outage and privacy tests. Jason Stys. |
| [tests/test\_live\_guards.py](tests/test_live_guards.py) | Cross-platform destructive-stage ownership, acknowledgment, deadline and TLS-copy contracts. Jason Stys. |
| [tests/test\_manager\_build.py](tests/test_manager_build.py) | Independent rejection oracles for maintained manager module/checksum identity. Created by Jason Stys. |
| [tests/test\_native\_inputs.py](tests/test_native_inputs.py) | Actual same-descriptor input bounds and ownership-change cases for selected offline reports. Jason Stys. |
| [tests/test\_profile\_admission.py](tests/test_profile_admission.py) | Actual pre-existing alias refusal and ordinary SQLite recovery continuity. Jason Stys. |
| [tests/test\_scanner.py](tests/test_scanner.py) | Scanner regression: actual post-build rootfs mode and nonempty Go inventory required. Created by Jason Stys. |
| [tests/test\_tk\_runtime.py](tests/test_tk_runtime.py) | Actual isolated native Tcl positive plus fail-closed loader/interpreter/version controls. Jason Stys. |
| [tools.lock.json](tools.lock.json) | Exact official release hashes and immutable PostgreSQL base image. |

<!-- END FILE GUIDE -->

## Maintenance and contribution

Run the full [validation commands](docs/testing.md), review actual security findings without suppressions, and rerun the real drill after lifecycle changes. Never paste tokens in issue bodies, publish ignored `out/` data or run this against a shared/production Docker host. Check account Actions storage before workflow work; cleanup needs fresh user approval and verified private backups. For bugs/security reporting and help, see [SECURITY](SECURITY.md), [CONTRIBUTING](CONTRIBUTING.md) and the runbook. Authored source is MIT; OpenBao and PostgreSQL retain their upstream licenses and trademarks.

## Documentation editions

Start with the [organized handbook](docs/handbook.md) for current usage, design, security and test guidance. Reviewed downloadable editions: [project-guide.docx](docs/reports/project-guide.docx).

[Publication identities and source scope](docs/reports/publications.json) · [Documentation validation record](docs/reports/documentation-refresh-2026-11-09.md). Historical results retain their own tested revision and date.


## Current installed application guide

The published **1.1.0** application has a [four-page guide](docs/reports/windows-application-guide-1.1.0-r2.docx) with actual installed screenshots, a practical journey, immutable source excerpts and operating limits. The [installed validation report](docs/reports/installed-windows-1.1.0-r2-2026-11-11.md) explains the results and [review manifest](docs/reports/windows-application-guide-1.1.0-r2.json) records exact source, image and page identities. Historical documentation remains available.
