# Secret Rotation Reliability Lab

[![Validate](https://github.com/JasonStys/secret-rotation-reliability-lab/actions/workflows/ci.yml/badge.svg)](https://github.com/JasonStys/secret-rotation-reliability-lab/actions/workflows/ci.yml)
[![CodeQL](https://github.com/JasonStys/secret-rotation-reliability-lab/actions/workflows/codeql.yml/badge.svg)](https://github.com/JasonStys/secret-rotation-reliability-lab/actions/workflows/codeql.yml)

Created by **Jason Stys** · [GitHub](https://github.com/JasonStys) · [LinkedIn](https://www.linkedin.com/in/jason-stys-31b30b351/)

A defensive DevOps lab that tests what happens **after a database password changes**: credential handoff, lease expiry, identity revocation and a secrets-manager outage. It uses a real OpenBao PostgreSQL secrets engine rather than inventing a password vault. Native deterministic/property/concurrency tests and a completely separate live TLS exercise distinguish a convincing demo from evidence.

This is an isolated learning/portfolio project, **not a production secrets service, military compliance certification, zero-downtime guarantee or authorization to touch someone else's infrastructure**. All data and credentials are fictional/disposable. The live drill refuses Windows/macOS and requires explicit acknowledgement on a disposable Linux Docker host. Local Docker Desktop is left unchanged.

## Features and major functions

| Component | What it demonstrates |
| --- | --- |
| `Lease` / `Policy` | Printable bounded credentials, strict int/bool rules, finite settings, conservative monotonic deadlines and early refresh. |
| `Broker.get` | One refresh for concurrent callers, finite capped retry, transient-only valid-cache fallback and strict expiry rejection. TLS/authorization/malformed-provider failures invalidate the cache immediately. |
| `Broker.invalidate` | A late failure on an old lease cannot erase a newer generation. Consumers must close/drain their old database connections. |
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
| [docs/contracts.md](docs/contracts.md) | Lifecycle, data and privacy contracts. |
| [docs/reports/validation.md](docs/reports/validation.md) | Measured validation and author review. |
| [docs/research.md](docs/research.md) | Primary-source research and implementation choices. |
| [docs/runbook.md](docs/runbook.md) | Runbook: safe local demonstration and owned live exercise. |
| [docs/testing.md](docs/testing.md) | Test strategy and reproducible validation. |
| [docs/threat-model.md](docs/threat-model.md) | Threat model and deployment limits. |
| [ops/reader.hcl](ops/reader.hcl) | Jason Stys: application token can issue ONLY reader credentials; everything else remains default-deny. |
| [ops/start-postgres.sh](ops/start-postgres.sh) | Jason Stys: bounded wait for owned, generated TLS fixture files, then exec the native PostgreSQL entrypoint. |
| [pyproject.toml](pyproject.toml) | Strict lint/type/test/statement-and-branch coverage configuration. |
| [requirements-dev.in](requirements-dev.in) | Exact portable development tool inputs. |
| [requirements-dev.lock](requirements-dev.lock) | Complete hash-locked portable development graph. |
| [requirements-integration.in](requirements-integration.in) | Exact live-only PostgreSQL driver input. |
| [requirements-integration.lock](requirements-integration.lock) | Hash-locked CPython3.14/Linux-x86_64 live-only driver graph. |
| [rotation/\_\_init\_\_.py](rotation/__init__.py) | Credential lifecycle contracts and safe evidence by Jason Stys; no import-time I/O. |
| [rotation/\_\_main\_\_.py](rotation/__main__.py) | Offline demo and strict aggregate inspection CLI; raw secrets/errors never printed. Created by Jason Stys. |
| [rotation/bao.py](rotation/bao.py) | Verified TLS, no redirects/proxies, bounded OpenBao JSON and safe provider errors. Created by Jason Stys. |
| [rotation/broker.py](rotation/broker.py) | Single-flight credential refresh with bounded retry, safe statistics and stale-lease guards. Jason Stys. |
| [rotation/contracts.py](rotation/contracts.py) | Bounded lease/policy contracts; secret fields never enter representations. Created by Jason Stys. |
| [rotation/evidence.py](rotation/evidence.py) | Allowlisted aggregate reports, inert escaped HTML and new-directory-only output. Created by Jason Stys. |
| [rotation/simulation.py](rotation/simulation.py) | Deterministic offline lifecycle demonstration, explicitly NOT live-manager evidence. Created by Jason Stys. |
| [scripts/\_\_init\_\_.py](scripts/__init__.py) | Opt-in disposable exercise and maintained-repository helpers by Jason Stys; no import-time I/O. |
| [scripts/bao\_check.py](scripts/bao_check.py) | Scan the actual verified OpenBao binary's Go module inventory with no advisory exclusions. Created by Jason Stys. |
| [scripts/benchmark.py](scripts/benchmark.py) | Measure warmed cached broker decisions with an independent one-issuance oracle. Created by Jason Stys. |
| [scripts/code\_map.py](scripts/code_map.py) | Generate/check exact Python, SQL, shell and YAML symbol positions. Created by Jason Stys. |
| [scripts/file\_guide.py](scripts/file_guide.py) | Maintain a complete tracked-file README purpose inventory; unknown file types fail closed. Created by Jason Stys. |
| [scripts/image\_check.py](scripts/image_check.py) | Build/scan a non-root-only image from the immutable official PostgreSQL base; do not suppress vulnerabilities. Jason Stys. |
| [scripts/live\_drill.py](scripts/live_drill.py) | Real TLS OpenBao/PostgreSQL lifecycle on an acknowledged disposable Linux Docker host. Created by Jason Stys. |
| [scripts/scanners.py](scripts/scanners.py) | Install only hash-pinned official Linux scanner binaries. Created by Jason Stys. |
| [scripts/validate.sh](scripts/validate.sh) | Jason Stys: strict portable tests and maintained source/documentation contracts; no Actions storage uploads. |
| [scripts/validate\_repo.py](scripts/validate_repo.py) | Gate immutable pins, workflow permission/storage and credential tracking invariants. Created by Jason Stys. |
| [sql/seed.sql](sql/seed.sql) | Jason Stys: fictional product inventory and dedicated non-superuser credential manager privileges. |
| [tests/test\_bao.py](tests/test_bao.py) | Provider protocol and transport adversarial tests; fake sockets never access outside networks. Jason Stys. |
| [tests/test\_broker.py](tests/test_broker.py) | Deterministic retry/expiry/identity/race tests plus actual concurrent single-flight threads. Jason Stys. |
| [tests/test\_contracts.py](tests/test_contracts.py) | Independent lease/policy boundary and fuzz/property tests; all values fictional. Created by Jason Stys. |
| [tests/test\_evidence.py](tests/test_evidence.py) | Strict evidence schema, output privacy, real CLI control flow and aggregate negative tests. Jason Stys. |
| [tests/test\_live\_guards.py](tests/test_live_guards.py) | Cross-platform destructive-stage ownership, acknowledgment, deadline and TLS-copy contracts. Jason Stys. |
| [tools.lock.json](tools.lock.json) | Exact official release hashes and immutable PostgreSQL base image. |

<!-- END FILE GUIDE -->

## Maintenance and contribution

Run the full [validation commands](docs/testing.md), review actual security findings without suppressions, and rerun the real drill after lifecycle changes. Never paste tokens in issue bodies, publish ignored `out/` data or run this against a shared/production Docker host. Check account Actions storage before workflow work; cleanup needs fresh user approval and verified private backups. For bugs/security reporting and help, see [SECURITY](SECURITY.md), [CONTRIBUTING](CONTRIBUTING.md) and the runbook. Authored source is MIT; OpenBao and PostgreSQL retain their upstream licenses and trademarks.
