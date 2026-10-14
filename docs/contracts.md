# Lifecycle, data and privacy contracts

Created by Jason Stys. Units are seconds unless explicitly milliseconds.

| Input/state | Contract |
| --- | --- |
| Endpoint | HTTPS with numeric `127.0.0.1`, explicit valid port, no credentials/path/query/fragment; standard hostname/certificate verification, TLS1.2+; no proxy/redirect support. |
| Credentials | Nonempty printable ASCII, bounded lengths; fixed `database/creds/reader/` lease namespace; no raw representation or automatic serialization. Python memory is not guaranteed zeroizable. |
| TTL | Exact int 3..3600; renewable exact bool. Starts at monotonic request initiation. Clock rollback/future start cannot make a cached lease usable. |
| Policy | Fraction0.1..0.9, guard0.1..30s, attempts exact int1..3; delay0..1s/max up to2s, max >= base. Bool/NaN/infinity rejected. Defaults0.6/1s/two attempts/0.05s/0.2s. |
| Broker | At most configured attempts, socket timeout2s/operation; lock serializes refresh. Fallback requires transient failure AND a fresh usability check. Nontransient failures invalidate even valid cache. |
| Invalidation | Only the identical failed lease can invalidate the current cache. A consumer closes/drains its own old DB connections; the broker is not a connection-pool implementation. |
| API JSON | Input/output64KiB, strict duplicate-key/nonfinite rejection; required fields typed; raw error bodies discarded. A trickling peer can extend wall-clock duration beyond the socket timeout; this fixed trusted-loopback fixture is not a transport for arbitrary providers. Production adaptation needs a total-deadline client and bounded provider execution. The hosted build/drill has a30-minute job deadline, with a15-minute compiler timeout. |
| Public report | Exact schema1/mode/source SHA/cases/counters; complete unique allowlisted cases; finite0..900000ms; bool outcomes and nonnegative exact integer counters. Unexpected fields (including secrets) reject the entire report. |
| Outputs | New non-symlink directories only, no overwrite. CLI reads only bounded regular non-symlink aggregates. Live data under repo `out/` is ignored and not publicly uploaded. |

HCL restricts the app token to credential issuance. The database manager has LOGIN/CREATEROLE but no SUPERUSER/CREATEDB; CONNECT/USAGE/SELECT grant options permit management of the fixed reader role only in this fictional database. CREATEROLE is powerful: the manager is not an application identity and needs strict production operational access. Database app identities receive no write/DDL or administrative permissions. The synthetic administrator exists solely for fixture setup and independent negative oracles.

Errors are `denied`, `invalid`, `tls`, or retryable `unavailable`. No untrusted provider message is a public category. Reports never include tokens, password verifiers, usernames, lease IDs, env files, root/unseal material, private keys or full manager/audit logs. Audit credential values are HMACed by OpenBao and tested; operational identifiers can remain in the raw audit log, which stays private. Hash checks authenticate consistency with reviewed upstream release metadata, not an independently verified signing identity.

Case reports distinguish `simulation` (eight offline assertions and simulated elapsed times) from `live` (15 actual service assertions and wall-clock observations). Performance numbers are informational machine-specific measurements; correctness and independent negative oracles are asserted separately. `source_sha` binds a report to executable-source Git revision, not a fabricated self-referential documentation commit.
