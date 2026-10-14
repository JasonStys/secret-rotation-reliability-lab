# Measured validation and author review

Created by Jason Stys. Native Windows and actual hosted Ubuntu3.12/3.14, Windows3.14 and Intel macOS3.14 validation on 2026-10-14 UTC: **96 tests pass in every lane**, with **98.83% combined statement/branch coverage** of authored `rotation/` modules, no skips or exclusions. Strict Ruff/mypy, maintained source maps/file inventory, complete portable/live dependency audits, Gitleaks history, actionlint and ShellCheck pass. Docker/build orchestration is outside that coverage denominator and is independently live-tested.

## Immutable executable-source acceptance

Source [9de4b265381a8820c86ed81c6cebf10d515a7653](https://github.com/JasonStys/secret-rotation-reliability-lab/commit/9de4b265381a8820c86ed81c6cebf10d515a7653) passed every job in [Validate38511996896](https://github.com/JasonStys/secret-rotation-reliability-lab/actions/runs/38511996896), completed 2026-10-14T04:37:18Z. Four native lanes, security and the actual service lane all succeeded. [CodeQL38511996929](https://github.com/JasonStys/secret-rotation-reliability-lab/actions/runs/38511996929) passed security-extended Python analysis; the open-alert API returned zero at 2026-10-14 04:41:25 UTC. [ci.json](ci.json) records the exact acceptance and selected supply-chain receipts.

Reports below are selected safe synthetic aggregates, not private keys/env files/raw audit logs. A report-only follow-up must pass these same **seven jobs** before final handoff; current README badges/Actions show main. This immutable runtime-source evidence does not fabricate a self-referential documentation-commit hash. No independent audit, production deployment or certification is claimed.

## Actual live service results

[live.json](live.json) was extracted from the completed real service job and validated with the exact public aggregate schema. [live.html](live.html) is generated from it, not handwritten success data. All **15 real cases** passed:

| Case | Duration ms | Independent evidence |
| --- | --- | --- |
| TLS | 2.555 | Wrong trust specifically fails certificate verification; correct manager trust works. |
| Bootstrap | 45.883 | Dedicated manager has CREATEROLE but no SUPERUSER/CREATEDB; fictional inventory/explicit grants and engine/policy setup succeed. |
| ACL | 11.195 | Anonymous, config, other-role and revoke paths are specifically denied. |
| Read-only | 19.376 | Two products/quantity19 match; WRITE fails with SQLSTATE42501. |
| Renewal | 14.072 | Real operator renewal endpoint returns a valid bounded TTL; fresh SQL works. The broker deliberately replaces rather than auto-renews credentials. |
| Overlap | 19.595 | Different old/new usernames/passwords both authenticate during controlled handoff. |
| Individual revocation | 33.144 | Exact old role loses access/is removed; new identity still reads; stale invalidation does not erase new cache. |
| Expiry | 4,070.856 | A real four-second credential initially reads, then loses authentication and its exact role is removed. |
| Manager-password rotation | 68.365 | Original dedicated manager login fails, verifier changes, administrator positive control works and fresh issuance still reads. |
| Outage grace | 2,013.174 | Owned stopped manager times out; still-valid cached credentials read successfully. |
| Outage expiry | 3,978.370 | After the conservative lifetime, manager timeout cannot return expired credentials. |
| Recovery | 24.904 | After resume, fresh issuance/new identity authenticates; old generation is not reused. |
| Identity revocation | 27.347 | App-token revocation cascades database lease removal; forced refresh denies and drops cache. |
| Redaction | 1.414 | Actual credential response password fields are HMACed; known tokens/passwords are absent from raw audit/server logs. Operational identifiers stay private. |
| Cleanup | 190.470 | Owned process terminates and exact freshly label/name-verified database container/network are removed; absence is verified. |

These stopwatches measure each assertion's action, **not** cold compilation/scans, TLS generation, server startup, whole-workflow latency, connection-pool drain or a production RTO/SLA. Renewal proves the real API's accepted returned TTL and immediate authorization, not an unmeasured guarantee of surviving beyond the original lifetime. The manager API binds loopback; PostgreSQL exposes no published port and uses only a checked private owned-subnet IP with verify-full certificate matching. The actual declarative audit exists and the default prohibition on API-created audit devices remains in effect and is specifically rejected.

## Actual security scans and performance scope

The lab-maintained pinned upstream rebuild uses Go1.27.2 and x/net0.60.0. Actual binary SHA-256 `41e1f7c63a6db24601f4d20612409d93fe94375533e4cd080e54d80aae7fccc9`: **292 Go packages, zero HIGH/CRITICAL findings**, with nonempty compiled inventory required. Actual derived non-root PostgreSQL image configuration ID `sha256:cff95c4df2c8d322377e5310676a47c91c8ce5cc9beeb96716c2fdd1e324e035` passed the full HIGH/CRITICAL gate. These are point-in-time dependency/image checks, not an independent source audit, signed build provenance or proof against future vulnerabilities. [Upstream-security notes](../upstream-security.md) explain the source/toolchain/module repair and license/provenance boundaries.

[benchmark.json](benchmark.json) measures five warmed Windows/Python3.14.6 batches of1,000 cached decisions: median **0.003884ms/decision**, peak Python allocation600bytes, exactly one issuance and5,000 identical cached return values. It excludes TLS/database/manager startup and is informational, not a comparative speedup or production throughput claim. Structural cached-decision complexity is O(1) within the bounded lab workload; cold refresh/validation bounds are documented in the ADR.

[simulation.json](simulation.json) / [simulation.html](simulation.html) separately label the eight offline assertions and **virtual** durations. Browser review confirmed readable attribution, table/caption and clear simulation scope; no scripts/forms/remote assets exist. This is not live evidence, and its source identity matches the accepted runtime.

## Development failures and author review

Historical new-lab failures remain online; none were deleted to make checks appear green.

- [38506810505](https://github.com/JasonStys/secret-rotation-reliability-lab/actions/runs/38506810505): source-filesystem scanning returned no Go binaries. The inventory gate rejected it; post-build rootfs scanning and empty/advisory-bearing regression tests corrected the mode.
- [38507228816](https://github.com/JasonStys/secret-rotation-reliability-lab/actions/runs/38507228816) / [38507636207](https://github.com/JasonStys/secret-rotation-reliability-lab/actions/runs/38507636207): actual stock-binary HIGH findings in Go1.27.1/x-net0.58.0. The pinned source rebuild fixes these; no packages/advisories/severities were excluded.
- [38508358447](https://github.com/JasonStys/secret-rotation-reliability-lab/actions/runs/38508358447), [38509034098](https://github.com/JasonStys/secret-rotation-reliability-lab/actions/runs/38509034098), [38509639528](https://github.com/JasonStys/secret-rotation-reliability-lab/actions/runs/38509639528): bootstrap audit API refused. Payload-free path/status/presence diagnostics and upstream-source inspection identified the protected API-creation default. Declarative HCL and a specific negative preserve the protection; no unsafe flag was enabled.
- [38510338990](https://github.com/JasonStys/secret-rotation-reliability-lab/actions/runs/38510338990): fixture setup failed around TLS delivery/port inspection. Generated two-file stdin tar delivery handles tmpfs without privileges. [38511032939](https://github.com/JasonStys/secret-rotation-reliability-lab/actions/runs/38511032939) exposed absent internal-network port mapping; the final design uses a checked owned IP and no DB publication, with public/loopback/out-of-subnet/wrong-network/published-endpoint regressions. The accepted full live run proves the resulting behavior.

Author-led code/architecture/testing/security review checked conservative expiry after retry latency, nontransient identity failure, exact-generation concurrency, duplicate JSON keys, no raw response/error publication, canonical output confinement/quoted config, real privilege/role-removal oracles, exact provenance receipts and fail-closed scan inventories. No external audit is represented.

- [x] Native tests/type/lint/maintained code+docs and explicitly scoped benchmark.
- [x] Actual TLS/SCRAM, least privilege, credential lifecycle/outage and audit/privacy assertions.
- [x] Corrected dependency/image/secrets/workflow/CodeQL gates and owned cleanup.
- [x] Selected safe measured reports; raw private material never uploaded.
- Final-main acceptance rule: report-only commits must pass the same hosted workflows before handoff.
- Production deployment, user data access, paid hosting and local Docker changes: not authorized/performed. CI creates zero Actions artifacts/caches; the separate earlier user-approved account cleanup remains separate from this repo's retained development history.
