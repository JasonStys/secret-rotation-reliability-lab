# ADR-001: delegated secrets management with a conservative consumer

Author: Jason Stys. Status: accepted for an isolated portfolio lab, 2026-10-14.

## Context and decision

A changed password is not a complete rotation. Consumers can cache old credentials, recreate too many leases concurrently, continue using an expired lease during an outage, or silently treat a denied identity as a transient failure. The lab needs independent native tests and real server/database evidence, without exposing credentials or using this PC's broken Docker installation.

Use OpenBao's existing PostgreSQL engine for creation/renewal/revocation, SQL for actual privileges, a typed standard-library Python consumer for concurrency/expiry behavior, HCL for a narrowly scoped token and Bash for fail-fast CI. A locked live-only Psycopg/native-libpq driver opens fresh verify-full TLS connections on a disposable Linux runner. Do not implement custom cryptography, a competing secrets store, a general external-host connector or production deployment automation.

The single-flight lock serializes refresh. Lease time begins **before** the HTTP call, so network latency never extends validity. Failed retries recheck the current monotonic clock before fallback. Only transient provider failures permit a still-valid cached lease; TLS/ACL/invalid data drop it immediately. Invalidation compares object identity to prevent old-generation failure races. The normal consumer replaces credentials; the drill separately proves the operator renewal API and inspects returned TTL instead of assuming the requested increment was granted.

## Alternatives and consequences

- Environment-variable/static passwords: simple, but no lifecycle/isolation proof. The database bootstrap env file is private/disposable, not the app's steady-state credentials.
- A custom manager: inappropriate security burden; generation/crypto/lease authority remain in OpenBao.
- Global catch-and-retry or indefinite stale fallback: hides revoked identity and violates expiry; rejected.
- New credentials on every request: correct but wastes manager/database capacity; single-flight cache issues once per generation.
- Remote production manager/HA: meaningful future work, not implied by this isolated experiment.

The fixed numeric-loopback manager transport removes DNS/proxy/redirect exfiltration surfaces but is deliberately not a production remote adapter. The live OpenBao process binds loopback and is terminated via its owned process handle. The database container is non-root/read-only/capability-dropped and uses resource-bounded tmpfs on an owned internal bridge with **no published database port**. Native clients use only its freshly identity-checked private IPv4 address inside the exact owned subnet; certificate SAN and verify-full checks match that address. TLS uses generated local trust, not certificate-verification bypass. The in-memory, one-share bootstrap loses all manager state on exit and is not an HA/backup/auto-unseal strategy.

## Cost and complexity

Cached decisions and counter updates are O(1) time/space; cold refresh makes at most three fixed-timeout requests and two capped sleeps, not an unbounded exponential loop. JSON bodies/reports are capped at 64 KiB; validation is O(n) within that bound. Reports contain fixed-size case/counter inventories. Concurrent refresh serializes waiters, so this is a teaching reference, not a high-throughput distributed cache. The benchmark measures warmed local decisions only, not database latency, cryptographic throughput or an optimization comparison.

## Verification

Native unit, Hypothesis, mocked transport and actual thread tests prove library boundaries. A separate real 15-case drill checks authorization/data behavior with positive controls, server-side role queries and HMAC audit entries. Docker helpers are not in the core coverage denominator and need real hosted integration. See [testing](testing.md) and [research sources](research.md). This decision does not assert a government certification, production approval or independent audit.
